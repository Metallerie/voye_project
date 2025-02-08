import requests
import json
import asyncio
from fastapi import FastAPI, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

# Connexion MongoDB
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "voye_db"
COLLECTION_NAME = "voye_config"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
config_collection = db[COLLECTION_NAME]

app = FastAPI()

class Processor:
    def __init__(self, file_content):
        """
        Initialise le processeur avec le contenu du fichier.
        """
        self.file_content = file_content
        self.api_key = None
        self.api_url = None

    async def load_config(self):
        """
        Charge l'URL et la clé API Mindee depuis MongoDB.
        """
        mindee_api_key = await config_collection.find_one({"key": "mindee_api_key"})
        mindee_api_url = await config_collection.find_one({"key": "mindee_api_url"})

        if mindee_api_key:
            self.api_key = mindee_api_key["value"]
        else:
            raise ValueError("Clé API Mindee introuvable dans MongoDB")

        if mindee_api_url:
            self.api_url = mindee_api_url["value"]
        else:
            raise ValueError("URL Mindee introuvable dans MongoDB")

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


            if "champs" not in data:
                raise ValueError("Réponse Mindee inattendue")

            return self.format_extracted_data(data)

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
            "fournisseur": raw_data.get("fournisseur", "Inconnu"),
            "version_format": raw_data.get("version_format", "1.0"),
            "champs": {}
        }

        # Extraction des champs
        champs = raw_data.get("champs", {})

        for key, value in champs.items():
            if isinstance(value, dict) and "polygon" in value:
                formatted_data["champs"][key] = {
                    "valeur": "Non défini",
                    "position": value["polygon"]
                }
            elif isinstance(value, list):
                formatted_data["champs"][key] = [
                    {"valeur": "Non défini", "position": item.get("polygon", [])}
                    for item in value
                ]
            else:
                formatted_data["champs"][key] = value

        return formatted_data


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
