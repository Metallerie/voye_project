import sys
import os
import json
import asyncio
import time
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from mindee_processor import Processor  # Extraction avec Mindee

# Connexion MongoDB
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "voye_db"
DOCUMENT_COLLECTION = "document_index"
PARTNER_COLLECTION = "partners_library"
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
documents_collection = db[DOCUMENT_COLLECTION]
partners_collection = db[PARTNER_COLLECTION]

# Définition des chemins
FACTURE_STORAGE_DIR = "/data/voye/filestore/account/factures/"
LIBRARY_DIR = "/data/voye/filestore/partner/library/"

class FactureProcessor:
    def __init__(self, filename):
        self.filename = filename
        self.partner_name = "unknown"
        self.library_path = None

    async def process(self):
        """
        Processus principal : extraction et sauvegarde des données de la facture.
        """
        print(f"📄 Traitement de la facture : {self.filename}")

        # Récupérer l'entrée du document dans MongoDB
        document_entry = await documents_collection.find_one({"filename": self.filename})
        if not document_entry:
            print("❌ Document non trouvé dans l'index !")
            return
        
        self.partner_name = document_entry.get("partner", "unknown")
        document_path = f"/data/voye/processed/{self.filename}"

        # Vérifier et charger la bibliothèque du partenaire
        self.library_path = os.path.join(LIBRARY_DIR, f"{self.partner_name}_facture_library.json")
        await self.ensure_library_exists()

        # Extraire les données avec Mindee
        extracted_data = await self.extract_invoice_data(document_path)
        if not extracted_data:
            print("❌ Aucune donnée extraite, abandon du traitement.")
            return

        # Sauvegarder les données extraites dans le bon dossier
        await self.save_extracted_data(extracted_data)

    async def ensure_library_exists(self):
        """
        Vérifie si une bibliothèque partenaire existe, sinon la crée.
        """
        if not os.path.exists(self.library_path):
            print(f"⚠️ Aucune bibliothèque trouvée pour {self.partner_name}, création en cours...")
            library_data = {"partner": self.partner_name, "document_type": "facture", "fields": {}}
            with open(self.library_path, "w", encoding="utf-8") as file:
                json.dump(library_data, file, ensure_ascii=False, indent=4)
            print(f"✅ Bibliothèque créée : {self.library_path}")

    async def extract_invoice_data(self, document_path):
        """
        Envoie le document à Mindee pour extraire les informations.
        """
        try:
            with open(document_path, "rb") as file:
                processor = Processor(file.read())
                print("🔄 Envoi à Mindee pour extraction...")
                return await processor.extract_data()
        except Exception as e:
            print(f"⚠️ Erreur d'extraction avec Mindee : {e}")
            return None

    async def save_extracted_data(self, extracted_data):
        """
        Sauvegarde les données extraites dans un fichier JSON structuré.
        """
        current_year = datetime.now().year
        facture_dir = os.path.join(FACTURE_STORAGE_DIR, str(current_year))
        os.makedirs(facture_dir, exist_ok=True)

        json_filename = f"{self.partner_name}_{int(time.time())}.json"
        json_path = os.path.join(facture_dir, json_filename)

        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)

        print(f"✅ Facture enregistrée : {json_path}")

# Lancement du traitement
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Erreur : Aucun fichier spécifié.")
        sys.exit(1)

    filename = sys.argv[1]
    processor = FactureProcessor(filename)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(processor.process())
