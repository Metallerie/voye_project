import json
import importlib
import os
import shutil
import sys
import time
import re
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pdf2image import convert_from_path, pdfinfo_from_path

# Connexion MongoDB
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "voye_db"
PARTNER_COLLECTION = "partners_library"
DOCUMENT_COLLECTION = "document_index"
CONFIG_COLLECTION = "voye_config"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
partners_collection = db[PARTNER_COLLECTION]
documents_collection = db[DOCUMENT_COLLECTION]
config_collection = db[CONFIG_COLLECTION]

class DocumentProcessor:
    def __init__(self, document_dir, processed_dir):
        self.document_dir = document_dir
        self.processed_dir = processed_dir

    async def process_all_documents(self):
        files = [f for f in os.listdir(self.document_dir) if f.endswith(".pdf")]
        for file in files:
            document_path = os.path.join(self.document_dir, file)
            if not os.path.exists(document_path):
                print(f"⚠️ Fichier introuvable : {document_path}")
                continue
            await self.process_document(document_path)

    async def process_document(self, document_path):
        print(f"🔍 Traitement du document : {document_path}")
        extracted_data = await self.extract_data(document_path)
        if not extracted_data:
            print("⚠️ Échec de l'extraction des données.")
            return
        
        partner_name = extracted_data.get("fournisseur", "unknown")
            self.api_key = mindee_api_key["value"]
        else:
            raise ValueError("Clé API Mindee introuvable dans MongoDB")

        if mindee_api_url:
            self.api_url = mindee_api_url["value"]
        else:
            raise ValueError("URL Mindee introuvable dans MongoDB")
        
        if locale_config:
            self.locale = locale_config["value"]
        
        if deepl_api_key:
            self.deepl_api_key = deepl_api_key["value"]
        else:
            raise ValueError("Clé API Mindee introuvable dans MongoDB")

        if mindee_api_url:
            self.api_url = mindee_api_url["value"]
        else:
            raise ValueError("URL Mindee introuvable dans MongoDB")
        
        if locale_config:
            self.locale = locale_config["value"]

    async def extract_data(self):
        """
        Envoie un document à Mindee et récupère les données extraites.
        """
        await self.load_config()  # Charge les paramètres API depuis MongoDB

        headers = {"Authorization": f"Token {self.api_key}"}

        try:
            files = {"document": ("facture.pdf", self.file_content, "application/pdf")}
            response = requests.post(self.api_url, headers=headers, files=files)

            response.raise_for_status()  # Vérifie si la requête a réussi
            data = response.json()
            
            # 🔴 DEBUG : Afficher la réponse complète de Mindee
            print("🔍 Réponse brute de Mindee :")
            print(json.dumps(data, indent=4, ensure_ascii=False))

            if "document" not in data:
                raise ValueError("Réponse Mindee inattendue")

            formatted_data = self.format_extracted_data(data["document"])
            translated_data = translate_dict(formatted_data, self.locale[:2])  # Traduction automatique
            await self.create_library(translated_data)
            return translated_data

        except requests.exceptions.RequestException as e:
            return {"error": f"Erreur API : {e}"}
        except ValueError as ve:
            return {"error": f"Erreur format de réponse : {ve}"}
        except Exception as e:
            return {"error": f"Erreur inattendue : {e}"}

    def format_extracted_data(self, raw_data):
        """
        Formate les données extraites pour une meilleure lisibilité.
        """
        formatted_data = {
            "fournisseur": raw_data.get("supplier", "Inconnu"),
            "version_format": raw_data.get("version_format", "1.0"),
            "champs": {}
        }

        # Extraction des champs
        champs = raw_data.get("inference", {}).get("prediction", {})

        for key, value in champs.items():
            if isinstance(value, dict) and "polygon" in value:
                formatted_data["champs"][key] = {
                    "valeur": value.get("value", "Non défini"),
                    "position": value["polygon"]
                }
            elif isinstance(value, list):
                formatted_data["champs"][key] = [
                    {"valeur": item.get("value", "Non défini"), "position": item.get("polygon", [])}
                    for item in value
                ]
            else:
                formatted_data["champs"][key] = value

        return formatted_data

    async def create_library(self, extracted_data):
        """
        Crée une bibliothèque pour le partenaire extrait après traduction.
        """
        partner_name = extracted_data.get("fournisseur", "unknown").replace(" ", "_").replace("/", "_")
        document_type = "facture"
        library_path = f"/data/voye/filestore/partner/library/{partner_name}_{document_type}_library.json"
        
        if not os.path.exists("/data/voye/filestore/partner/library/"):
            os.makedirs("/data/voye/filestore/partner/library/")
        
        with open(library_path, "w", encoding="utf-8") as file:
            json.dump(extracted_data, file, ensure_ascii=False, indent=4)
        
        print(f"✅ Bibliothèque créée : {library_path}")
        await partner_library_collection.update_one(
            {"name": partner_name},
            {"$set": {"library_path": library_path}},
            upsert=True
        )

# --- Endpoint FastAPI pour traiter un fichier ---
@app.post("/extract/")
async def extract_invoice(file: UploadFile = File(...)):
    """
    Endpoint pour extraire les données d'une facture.
    """
    file_content = await file.read()  # Lire le fichier envoyé
    processor = Processor(file_content)
    
    result = await processor.extract_data()
    
    return result
