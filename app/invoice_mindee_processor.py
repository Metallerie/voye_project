import os
import json
import logging
import datetime
import hashlib
from mindee import Client, product
from pymongo import MongoClient

# Configuration du logger
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# Connexion à MongoDB pour récupérer les configurations
def get_config():
    with MongoClient("mongodb://localhost:27017/") as client:
        db = client["voye_db"]
        collection = db["voye_config"]
        return {item["key"]: item["value"] for item in collection.find()}

config = get_config()
API_KEY = config.get("mindee_api_key", "")
INPUT_DIRECTORY = config.get("input_directory", "/data/voye/document/")
INVOICE_STORAGE_PATH = config.get("invoice_storage_path", "/data/voye/filestore/account/invoice/")
ARCHIVE_DIRECTORY = config.get("archive_directory", "/data/voye/archive/invoice/")
ERROR_DIRECTORY = config.get("error_directory", "/data/voye/document/document_error/")

# Fonction pour calculer le hash MD5 du fichier
def calculate_file_hash(file_path, hash_algorithm="md5"):
    hash_func = hashlib.md5() if hash_algorithm == "md5" else hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

# Fonction pour extraire les informations d'un PDF et créer un fichier JSON
def extract_and_create_json(pdf_path, filename):
    try:
        mindee_client = Client(api_key=API_KEY)
    except Exception as e:
        _logger.error(f"Échec de l'initialisation du client Mindee: {e}")
        return False, None, None, None, None, None, None, None

    try:
        with open(pdf_path, "rb") as f:
            input_doc = mindee_client.source_from_file(f)
            api_response = mindee_client.parse(product.InvoiceV4, input_doc)
        
        if not hasattr(api_response, 'document') or api_response.document is None:
            _logger.error(f"Erreur Mindee : Impossible d'extraire le document {pdf_path}")
            return False, None, None, None, None, None, None, None
    except Exception as e:
        _logger.error(f"Erreur lors de la lecture du document {pdf_path}: {e}")
        error_path = os.path.join(ERROR_DIRECTORY, filename)
        os.makedirs(ERROR_DIRECTORY, exist_ok=True)
        os.rename(pdf_path, error_path)
        _logger.info(f"Document déplacé dans le dossier d'erreur : {error_path}")
        return False, None, None, None, None, None, None, None

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
    
    partner_name = extracted_data.get("supplier_name") or extracted_data.get("company_name", "Unknown")
    document_date = extracted_data.get("date") or extracted_data.get("invoice_date", "Unknown")
    
    current_year = datetime.datetime.now().year
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_directory = os.path.join(INVOICE_STORAGE_PATH, str(current_year))
    os.makedirs(output_directory, exist_ok=True)
    
    json_filename = os.path.join(output_directory, f"{timestamp}.json")
    
    file_size = os.path.getsize(pdf_path)
    file_hash = calculate_file_hash(pdf_path, "md5")
    extracted_data["checksum"] = file_hash
    
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)
    
    _logger.info(f"Fichier JSON créé : {json_filename}")
    return True, json_filename, INVOICE_STORAGE_PATH, ARCHIVE_DIRECTORY, partner_name, document_date, file_size, file_hash

if __name__ == "__main__":
    if not os.path.exists(INPUT_DIRECTORY):
        _logger.error(f"Le répertoire d'entrée {INPUT_DIRECTORY} n'existe pas.")
    else:
        with MongoClient("mongodb://localhost:27017/") as client:
            db = client["voye_db"]
            index_collection = db["index_document"]
            
            for filename in os.listdir(INPUT_DIRECTORY):
                if filename.lower().endswith(".pdf"):
                    pdf_path = os.path.join(INPUT_DIRECTORY, filename)
                    file_hash = calculate_file_hash(pdf_path, "md5")
                    
                    # Vérifier si le document est déjà indexé
                    existing_doc = index_collection.find_one({"checksum": file_hash})
                    if existing_doc:
                        _logger.warning(f"Document déjà indexé : {filename} (checksum identique), suppression du fichier.")
                        os.remove(pdf_path)
                        continue
                    
                    _logger.info(f"Traitement du fichier : {pdf_path}")
                    result = extract_and_create_json(pdf_path, filename)
                    
                    if result[0]:
                        success, json_filename, storage_path, archive_path, partner_name, document_date, file_size, file_hash = result
                        _logger.info(f"Fichier traité avec succès : {filename}")
                        archive_path = os.path.join(archive_path, str(datetime.datetime.now().year))
                        os.makedirs(archive_path, exist_ok=True)
                        os.rename(pdf_path, os.path.join(archive_path, filename))
                        _logger.info(f"Fichier d'origine déplacé dans : {archive_path}")
                        
                        document_index = {
                            "original_filename": filename,
                            "document_type": "invoice",
                            "json_filename": json_filename,
                            "storage_path": storage_path,
                            "archive_path": archive_path,
                            "partner_name": partner_name,
                            "document_date": document_date,
                            "file_size": file_size,
                            "checksum": file_hash,
                            "timestamp": datetime.datetime.now()
                        }
                        index_collection.insert_one(document_index)
                        _logger.info(f"Document indexé dans MongoDB : {filename}")
                    else:
                        _logger.error(f"Échec du traitement : {filename}")
