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
        self.api_key = None
        self.api_url = None
        self.locale = "fr_FR"
        self.deepl_api_key = None

    async def load_config(self):
        """
        Charge les clés API et configurations depuis MongoDB.
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
            raise ValueError("Clé API DeepL introuvable dans MongoDB")

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
        document_type = "facture"
        
        # Stocker l'index du document dans MongoDB
        await self.index_document_in_db(document_path, partner_name, document_type)
        
        self.move_processed_file(document_path)

    async def extract_data(self, document_path):
        from mindee_processor import Processor
        try:
            with open(document_path, "rb") as file:
                processor = Processor(file.read())
                return await processor.extract_data()
        except Exception as e:
            print(f"⚠️ Erreur inattendue : {e}")
            return None
    
    async def index_document_in_db(self, document_path, partner_name, document_type):
        document_entry = {
            "filename": os.path.basename(document_path),
            "partner": partner_name,
            "document_type": document_type,
            "timestamp": int(time.time())
        }
        await documents_collection.insert_one(document_entry)
        print(f"✅ Document indexé dans MongoDB : {document_entry}")
    
    def move_processed_file(self, document_path):
        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)
        dest_path = os.path.join(self.processed_dir, os.path.basename(document_path))
        shutil.move(document_path, dest_path)
        print(f"✅ Fichier déplacé vers {dest_path}")
    
# Exemple d'utilisation
if __name__ == "__main__":
    print("🚀 Démarrage du traitement des documents...")
    processor = DocumentProcessor(
        "/data/voye/document/",
        "/data/voye/processed/"
    )
