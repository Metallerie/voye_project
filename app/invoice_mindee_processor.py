import os
import json
import logging
import datetime
from mindee import Client, product
from pymongo import MongoClient

# Configuration du logger
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# Connexion à MongoDB pour récupérer les configurations
def get_config():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["voye_db"]
    collection = db["voye_config"]
    config_data = {item["key"]: item["value"] for item in collection.find()}
    client.close()
    return config_data

config = get_config()
API_KEY = config.get("mindee_api_key", "")
INPUT_DIRECTORY = config.get("input_directory", "/data/voye/document/")
INVOICE_STORAGE_PATH = config.get("invoice_storage_path", "/data/voye/filestore/account/invoice/")
ARCHIVE_DIRECTORY = config.get("archive_directory", "/data/voye/archive/invoice/")

# Connexion à MongoDB pour stocker l'indexation des documents
client = MongoClient("mongodb://localhost:27017/")
db = client["voye_db"]
index_collection = db["index_document"]

# Fonction pour extraire les informations d'un PDF et créer un fichier JSON
def extract_and_create_json(pdf_path, filename):
    try:
        mindee_client = Client(api_key=API_KEY)
    except Exception as e:
        _logger.error(f"Échec de l'initialisation du client Mindee: {e}")
        return False, None

    try:
        with open(pdf_path, "rb") as f:
            input_doc = mindee_client.source_from_file(f)
            api_response = mindee_client.parse(product.InvoiceV4, input_doc)
    except Exception as e:
        _logger.error(f"Erreur lors de la lecture du document {pdf_path}: {e}")
        return False, None

    document = api_response.document
    extracted_data = {}
    
    # Extraire toutes les données disponibles
    for field, value in document.inference.prediction.__dict__.items():
        if isinstance(value, list):
            extracted_data[field] = [
                {k: v.value if hasattr(v, 'value') else v for k, v in item.__dict__.items()}
                for item in value
            ]
        elif hasattr(value, 'value'):
            extracted_data[field] = value.value
        else:
            extracted_data[field] = value
    
    # Définir l'année en cours et un index temporel précis
    current_year = datetime.datetime.now().year
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_directory = os.path.join(INVOICE_STORAGE_PATH, str(current_year))
    os.makedirs(output_directory, exist_ok=True)
    
    json_filename = os.path.join(output_directory, f"{timestamp}.json")
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)

    _logger.info(f"Fichier JSON créé : {json_filename}")
    return True, json_filename, INVOICE_STORAGE_PATH, ARCHIVE_DIRECTORY

# Traiter tous les fichiers présents dans le dossier d'entrée
if __name__ == "__main__":
    if not os.path.exists(INPUT_DIRECTORY):
        _logger.error(f"Le répertoire d'entrée {INPUT_DIRECTORY} n'existe pas.")
    else:
        for filename in os.listdir(INPUT_DIRECTORY):
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(INPUT_DIRECTORY, filename)
                _logger.info(f"Traitement du fichier : {pdf_path}")
                success, json_filename, storage_path, archive_path = extract_and_create_json(pdf_path, filename)
                if success:
                    _logger.info(f"Fichier traité avec succès : {filename}")
                    archive_path = os.path.join(archive_path, str(datetime.datetime.now().year))
                    os.makedirs(archive_path, exist_ok=True)
                    os.rename(pdf_path, os.path.join(archive_path, filename))
                    _logger.info(f"Fichier d'origine déplacé dans : {archive_path}")
                    
                    # Indexer le document dans MongoDB
                    document_index = {
                        "original_filename": filename,
                        "document_type": "invoice",  # Ce type peut être déduit plus tard
                        "json_filename": json_filename,
                        "storage_path": storage_path,
                        "archive_path": archive_path,
                        "timestamp": datetime.datetime.now()
                    }
                    index_collection.insert_one(document_index)
                    _logger.info(f"Document indexé dans MongoDB : {filename}")
                else:
                    _logger.error(f"Echec du traitement : {filename}")
