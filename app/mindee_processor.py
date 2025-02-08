import json
import importlib
import os
import shutil
import sys
import time
import re
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Connexion MongoDB
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "voye_db"
PARTNER_COLLECTION = "partners_library"
DOCUMENT_COLLECTION = "document_index"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
partners_collection = db[PARTNER_COLLECTION]
documents_collection = db[DOCUMENT_COLLECTION]

class DocumentProcessor:
    def __init__(self, document_dir, processed_dir, filestore_dir):
        self.document_dir = document_dir
        self.processed_dir = processed_dir
        self.filestore_dir = filestore_dir

    async def process_all_documents(self):
        files = [f for f in os.listdir(self.document_dir) if f.endswith(".pdf")]
        for file in files:
            document_path = os.path.join(self.document_dir, file)
            await self.process_document(document_path)

    async def process_document(self, document_path):
        print(f"🔍 Traitement du document : {document_path}")
        extracted_data = await self.extract_data(document_path)
        if not extracted_data:
            print("⚠️ Échec de l'extraction des données.")
            return
        
        partner_name = self.extract_partner_name(extracted_data).replace(" ", "_").replace("/", "_")
        document_type = self.detect_document_type(extracted_data)
        
        # Vérifier si une bibliothèque existe pour ce partenaire
        library_path = f"/data/voye/filestore/partner/library/{partner_name}_{document_type}_library.json"
        if not os.path.exists(library_path):
            print(f"📂 Bibliothèque introuvable pour {partner_name}, création avec Mindee...")
            await self.create_library_with_mindee(document_path, library_path)
        
        # Stocker l'index du document dans MongoDB
        await self.index_document_in_db(document_path, partner_name, document_type)
        
        self.move_processed_file(document_path)

    async def extract_data(self, document_path):
        from mindee_processor import Processor
        with open(document_path, "rb") as file:
            processor = Processor(file.read())
            return await processor.extract_data()

    def extract_partner_name(self, data):
        if "fournisseur" in data and data["fournisseur"]:
            return data["fournisseur"].strip()
        return "unknown"
    
    def detect_document_type(self, data):
        if "ticket" in data.get("text", "").lower():
            return "ticket"
        return "facture"
    
    async def create_library_with_mindee(self, document_path, library_path):
        extracted_data = await self.extract_data(document_path)
        with open(library_path, "w", encoding="utf-8") as file:
            json.dump(extracted_data, file, ensure_ascii=False, indent=4)
        print(f"✅ Bibliothèque créée : {library_path}")
    
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
        "/data/voye/processed/",
        "/data/voye/filestore/account/factures/2025/"
    )
    asyncio.run(processor.process_all_documents())
