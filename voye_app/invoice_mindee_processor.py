import os
import json
import logging
import datetime
import hashlib
from mindee import Client, product
from pymongo import MongoClient

# Configuration du logger pour afficher les messages d'information et d'erreur
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# Fonction pour récupérer la configuration depuis MongoDB
# La table `voye_config` stocke les paramètres globaux du système, tels que les chemins d'accès et la clé API Mindee

def get_config():
    with MongoClient("mongodb://localhost:27017/") as client:
        db = client["voye_db"]
        collection = db["voye_config"]
        return {item["key"]: item["value"] for item in collection.find()}

# Chargement de la configuration depuis la base de données `voye_config`
config = get_config()
API_KEY = config.get("mindee_api_key", "")

# Définition des répertoires utilisés dans le projet
INPUT_DIRECTORY = config.get("input_directory", "/data/voye/document/")  # Répertoire d'entrée des documents PDF à traiter
INVOICE_STORAGE_PATH = config.get("invoice_storage_path", "/data/voye/filestore/account/invoice/")  # Stockage des factures traitées en JSON
ARCHIVE_DIRECTORY = config.get("archive_directory", "/data/voye/archive/invoice/")  # Archive des fichiers PDF après traitement
ERROR_DIRECTORY = config.get("error_directory", "/data/voye/document/document_error/")  # Stockage des fichiers non traitables

# Fonction pour calculer le hash d'un fichier (MD5 ou SHA256)
# Utile pour identifier les doublons et assurer l'intégrité des fichiers

def calculate_file_hash(file_path, hash_algorithm="md5"):
    hash_func = hashlib.md5() if hash_algorithm == "md5" else hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

# Fonction pour extraire les informations d'une facture PDF via l'API Mindee
# Elle crée un fichier JSON contenant les données extraites et l'enregistre dans le stockage défini

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
    
    # Extraction des données sous forme de dictionnaire
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
    
    # Récupération des informations essentielles pour l'indexation
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

# Fonction principale pour traiter les fichiers dans le dossier d'entrée
if __name__ == "__main__":
    if not os.path.exists(INPUT_DIRECTORY):
        _logger.error(f"Le répertoire d'entrée {INPUT_DIRECTORY} n'existe pas.")
    else:
        with MongoClient("mongodb://localhost:27017/") as client:
            db = client["voye_db"]
            index_collection = db["index_document"]  # index_document est la colone vertébrale du projet 
            tous les document traités sont indexé dans cette table, chaque document est attaché à un index temporel très précis de leur entré dans le système 
            elle Stocke les métadonnées des documents traités pour éviter les doublons.
            
            # Parcours des fichiers PDF dans le dossier d'entrée
            for filename in os.listdir(INPUT_DIRECTORY):
                if filename.lower().endswith(".pdf"):
                    pdf_path = os.path.join(INPUT_DIRECTORY, filename)
                    file_hash = calculate_file_hash(pdf_path, "md5")
                    
                    # Vérification si le fichier est déjà indexé dans `index_document`
                    existing_doc = index_collection.find_one({"checksum": file_hash})
                    if existing_doc:
                        _logger.warning(f"Document déjà indexé : {filename} (checksum identique), suppression du fichier.")
                        os.remove(pdf_path)
                        continue
