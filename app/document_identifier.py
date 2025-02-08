import asyncio
import os
import time
import re
from motor.motor_asyncio import AsyncIOMotorClient

# Connexion MongoDB
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "voye_db"
DOCUMENT_COLLECTION = "document_index"
CONFIG_COLLECTION = "voye_config"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
documents_collection = db[DOCUMENT_COLLECTION]
config_collection = db[CONFIG_COLLECTION]

class DocumentIdentifier:
    def __init__(self, document_dir, processed_dir):
        self.document_dir = document_dir
        self.processed_dir = processed_dir
        self.document_keywords = {}

    async def load_config(self):
        """
        Charge les mots-clés de type de document depuis MongoDB.
        """
        config = await config_collection.find_one({"key": "document_keywords"})
        if config and "value" in config:
            self.document_keywords = config["value"]
        else:
            print("⚠️ Aucun mot-clé trouvé pour identifier les documents !")

    async def identify_and_process_documents(self):
        """
        Identifie et traite tous les documents présents dans le dossier.
        """
        await self.load_config()  # Charger la config des mots-clés

        files = [f for f in os.listdir(self.document_dir) if f.endswith(".pdf")]
        if not files:
            print("⚠️ Aucun fichier PDF trouvé dans le dossier.")
            return

        print(f"📂 {len(files)} fichier(s) détecté(s) :")
        for file in files:
            print(f"   - {file}")
            await self.process_document(file)

    async def process_document(self, filename):
        """
        Traite un document : identification du type et enregistrement.
        """
        document_path = os.path.join(self.document_dir, filename)

        # Charger le texte brut pour analyse
        extracted_text = await self.extract_text_from_pdf(document_path)
        doc_type = await self.identify_document_type(filename, extracted_text)

        # Stocker l'index du document
        document_entry = {
            "filename": filename,
            "document_type": doc_type,
            "timestamp": int(time.time())
        }
        await documents_collection.insert_one(document_entry)
        print(f"✅ Document indexé : {document_entry}")

        # Déplacer le fichier après traitement
        self.move_processed_file(document_path)

    async def extract_text_from_pdf(self, document_path):
        """
        Extrait le texte d'un PDF avec une méthode OCR basique.
        """
        from pdf2image import convert_from_path
        import pytesseract

        text = ""
        try:
            images = convert_from_path(document_path)
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction du texte : {e}")
        
        return text.strip()

    async def identify_document_type(self, filename, extracted_text):
        """
        Identifie le type de document en utilisant :
        1. Le nom de fichier (si possible).
        2. L'analyse du texte extrait.
        """
        doc_type = self.identify_type_from_filename(filename)
        if doc_type == "autre":
            doc_type = await self.identify_type_from_text(extracted_text)
        return doc_type

    def identify_type_from_filename(self, filename):
        """
        Détection rapide par nom de fichier.
        """
        filename = filename.lower()
        if re.search(r'\bfacture\b|\binvoice\b', filename):
            return "facture"
        elif re.search(r'\brib\b', filename):
            return "rib"
        elif re.search(r'\bkbis\b', filename):
            return "kbis"
        return "autre"

    async def identify_type_from_text(self, text):
        """
        Identification du type en analysant le texte extrait avec les mots-clés de `voye_config`.
        """
        for doc_type, words in self.document_keywords.items():
            if any(word.lower() in text.lower() for word in words):
                return doc_type
        return "autre"

    def move_processed_file(self, document_path):
        """
        Déplace le fichier traité vers le dossier des documents archivés.
        """
        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)
        dest_path = os.path.join(self.processed_dir, os.path.basename(document_path))
        os.rename(document_path, dest_path)
        print(f"✅ Fichier déplacé vers {dest_path}")

# Lancement du script
if __name__ == "__main__":
    print("🚀 Démarrage de l'identification des documents...")
    identifier = DocumentIdentifier("/data/voye/document/", "/data/voye/processed/")

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(identifier.identify_and_process_documents())
