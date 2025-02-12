import os
import shutil
import logging
from pymongo import MongoClient

# Configuration du logger
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["voye_db"]
index_collection = db["index_document"]

# Chemins des répertoires
invoice_path = "/data/voye/filestore/account/invoice/2025/"
archive_path = "/data/voye/archive/invoice/2025/"
document_path = "/data/voye/document/"

# Supprimer les fichiers de invoice_path
if os.path.exists(invoice_path):
    for filename in os.listdir(invoice_path):
        file_path = os.path.join(invoice_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            _logger.info(f"Supprimé : {file_path}")
else:
    _logger.warning(f"Le dossier {invoice_path} n'existe pas.")

# Déplacer les fichiers de archive_path vers document_path
if os.path.exists(archive_path):
    os.makedirs(document_path, exist_ok=True)
    for filename in os.listdir(archive_path):
        src = os.path.join(archive_path, filename)
        dst = os.path.join(document_path, filename)
        if os.path.isfile(src):
            shutil.move(src, dst)
            _logger.info(f"Déplacé : {src} → {dst}")
else:
    _logger.warning(f"Le dossier {archive_path} n'existe pas.")

# Vider la table index_document
deleted_count = index_collection.delete_many({}).deleted_count
_logger.info(f"Supprimé {deleted_count} entrées de la collection index_document.")

# Fermer la connexion MongoDB
client.close()
