import os
import json
from mindee import Client, product
import logging
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

# Fonction pour extraire les informations d'un PDF et créer un fichier JSON
def extract_and_create_json(pdf_path):
    try:
        mindee_client = Client(api_key=API_KEY)
    except Exception as e:
        _logger.error(f"Échec de l'initialisation du client Mindee: {e}")
        return False

    try:
        with open(pdf_path, "rb") as f:
            input_doc = mindee_client.source_from_file(f)
            api_response = mindee_client.parse(product.InvoiceV4, input_doc)
    except Exception as e:
        _logger.error(f"Erreur lors de la lecture du document {pdf_path}: {e}")
        return False

    document = api_response.document
    extracted_data = {}
    
    # Extraire toutes les données disponibles
    for field, value in document.inference.prediction.__dict__.items():
        if hasattr(value, 'value'):
            extracted_data[field] = value.value
        else:
            extracted_data[field] = value
    
    json_filename = os.path.splitext(os.path.basename(pdf_path))[0] + ".json"
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)

    _logger.info(f"Fichier JSON créé : {json_filename}")
    return True

# Exemple d'utilisation
if __name__ == "__main__":
    pdf_path = os.path.join(INPUT_DIRECTORY, "Facture_CCL_130616.pdf")  # Chemin de votre fichier PDF
    if os.path.exists(pdf_path):
        extract_and_create_json(pdf_path)
    else:
        _logger.error(f"Le fichier PDF {pdf_path} n'existe pas.")
