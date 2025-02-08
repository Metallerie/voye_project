import os
import json
import time
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# Connexion MongoDB
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "voye_db"
DOCUMENT_COLLECTION = "document_index"
CONFIG_COLLECTION = "voye_config"
PARTNER_COLLECTION = "partners_library"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
document_collection = db[DOCUMENT_COLLECTION]
config_collection = db[CONFIG_COLLECTION]
partner_collection = db[PARTNER_COLLECTION]

class DocumentIdentifier:

    def __init__(self, document_dir, processed_dir):
        self.document_dir = document_dir
        self.processed_dir = processed_dir
        self.document_types = {}
    async def load_document_keywords():
       config = await config_collection.find_one({"key": "document_keywords"})
       if config and "value" in config:
            return config["value"]
       return {}
    
    async def load_config(self):
        """Charge les types de documents dynamiquement depuis MongoDB"""
        config = await config_collection.find_one({"key": "document_types"})
        if config:
            self.document_types = config["value"]
        else:
            raise ValueError("⚠️ Aucun type de document trouvé dans voye_config.")
    
    async def identify_and_process_documents(self):
        """Analyse tous les documents du dossier et les traite."""
        files = [f for f in os.listdir(self.document_dir) if f.endswith(".pdf")]
        if not files:
            print("⚠️ Aucun fichier PDF trouvé.")
            return

        print(f"📂 {len(files)} fichier(s) détecté(s) :")
        for file in files:
            print(f"   - {file}")
            await self.process_document(file)

    async def process_document(self, filename):
        """Identifie le type et le partenaire avant d'appeler le bon script."""
        document_path = os.path.join(self.document_dir, filename)
        document_type = await self.detect_document_type(filename)
        partner = await self.identify_partner(filename)

        document_entry = {
            "filename": filename,
            "partner": partner,
            "document_type": document_type,
            "timestamp": int(time.time())
        }
        await document_collection.insert_one(document_entry)
        print(f"✅ Document indexé : {document_entry}")

        await self.call_document_processor(document_type, document_path)
        self.move_processed_file(document_path)
    
    async def detect_document_type(self, filename):
        """Détermine le type de document basé sur son nom et son contenu."""
        if "facture" in filename.lower():
            return "facture"
        elif "rib" in filename.lower():
            return "rib"
        elif "kbis" in filename.lower():
            return "kbis"
        return "autre"

    async def identify_partner(self, filename):
        """Identifie l'émetteur du document (fournisseur, client)."""
        partner = await partner_collection.find_one({"filename": filename})
        if partner:
            return partner["name"]
        return "unknown"
    
    async def call_document_processor(self, document_type, document_path):
        """Appelle dynamiquement le bon script de traitement."""
        script_name = self.document_types.get(document_type, "default_processor.py")
        print(f"🔄 Lancement de {script_name} pour {document_path}...")
        os.system(f"python3 {script_name} {document_path}")
    
    def move_processed_file(self, document_path):
        """Déplace le fichier après traitement."""
        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)
        dest_path = os.path.join(self.processed_dir, os.path.basename(document_path))
        os.rename(document_path, dest_path)
        print(f"✅ Fichier déplacé vers {dest_path}")

if __name__ == "__main__":
    print("🚀 Démarrage de l'identification des documents...")
    identifier = DocumentIdentifier("/data/voye/document/", "/data/voye/processed/")
    
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(identifier.identify_and_process_documents())

