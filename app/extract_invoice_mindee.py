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
    partner_name = (
        document.inference.prediction.supplier_name.value
        if hasattr(document.inference.prediction.supplier_name, 'value') else document.inference.prediction.supplier_name
        if document.inference.prediction.supplier_name else "Nom Inconnu"
    )
    partner_address = (
        document.inference.prediction.supplier_address.value
        if hasattr(document.inference.prediction.supplier_address, 'value') else document.inference.prediction.supplier_address
        if document.inference.prediction.supplier_address else "Adresse non fournie"
    )

    line_items = document.inference.prediction.line_items or []
    lines = []

    for item in line_items:
        description = item.description.value if hasattr(item.description, 'value') else item.description if item.description else "Description non fournie"
        unit_price = item.unit_price.value if hasattr(item.unit_price, 'value') else item.unit_price if item.unit_price else 0.0
        quantity = item.quantity.value if hasattr(item.quantity, 'value') else item.quantity if item.quantity else 1
        tax_rate = item.tax_rate.value if hasattr(item.tax_rate, 'value') else item.tax_rate if item.tax_rate else 0.0

        line_data = {
            "description": description,
            "unit_price": unit_price,
            "quantity": quantity,
            "tax_rate": tax_rate,
        }
        lines.append(line_data)

    document_total_net = document.inference.prediction.total_net.value if hasattr(document.inference.prediction.total_net, 'value') else document.inference.prediction.total_net if document.inference.prediction.total_net else 0.0
    document_total_amount = document.inference.prediction.total_amount.value if hasattr(document.inference.prediction.total_amount, 'value') else document.inference.prediction.total_amount if document.inference.prediction.total_amount else 0.0
    document_total_tax = document.inference.prediction.total_tax.value if hasattr(document.inference.prediction.total_tax, 'value') else document.inference.prediction.total_tax if document.inference.prediction.total_tax else 0.0

    invoice_data = {
        "partner_name": partner_name,
        "partner_address": partner_address,
        "invoice_date": document.inference.prediction.date.value if hasattr(document.inference.prediction.date, 'value') else document.inference.prediction.date if document.inference.prediction.date else None,
        "invoice_date_due": document.inference.prediction.due_date.value if hasattr(document.inference.prediction.due_date, 'value') else document.inference.prediction.due_date if document.inference.prediction.due_date else None,
        "invoice_number": document.inference.prediction.invoice_number.value if hasattr(document.inference.prediction.invoice_number, 'value') else document.inference.prediction.invoice_number if document.inference.prediction.invoice_number else "Référence inconnue",
        "line_items": lines,
        "total_net": document_total_net,
        "total_tax": document_total_tax,
        "total_amount": document_total_amount,
    }

    json_filename = os.path.splitext(os.path.basename(pdf_path))[0] + ".json"
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(invoice_data, json_file, ensure_ascii=False, indent=4)

    _logger.info(f"Fichier JSON créé : {json_filename}")
    return True

# Exemple d'utilisation
if __name__ == "__main__":
    pdf_path = os.path.join(INPUT_DIRECTORY, "Facture_CCL_130616.pdf")  # Chemin de votre fichier PDF
    if os.path.exists(pdf_path):
        extract_and_create_json(pdf_path)
    else:
        _logger.error(f"Le fichier PDF {pdf_path} n'existe pas.")
