import requests
import json
import asyncio
import os
from fastapi import FastAPI, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

# Connexion MongoDB
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "voye_db"
CONFIG_COLLECTION = "voye_config"
PARTNER_LIBRARY_COLLECTION = "partners_library"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
config_collection = db[CONFIG_COLLECTION]
partner_library_collection = db[PARTNER_LIBRARY_COLLECTION]

app = FastAPI()

class Processor:
    def __init__(self, file_content):
        """
        Initialise le processeur avec le contenu du fichier.
        """
        self.file_content = file_content
        self.api_key = None
        self.api_url = None
        self.locale = "fr_FR"  # Par défaut, utiliser le français
        self.deepl_api_key = None

    async def load_config(self):
        """
        Charge l'URL et les clés API Mindee et DeepL depuis MongoDB.
        """
        mindee_api_key = await config_collection.find_one({"key": "mindee_api_key"})
        mindee_api_url = await config_collection.find_one({"key": "mindee_api_url"})
        locale_config = await config_collection.find_one({"key": "icu_locale"})
        deepl_api_key = await config_collection.find_one({"key": "deepl_api_key"})

        if mindee_api_key:
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
