import os
import json
from mindee import Client, product
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# Clé API Mindee
API_KEY = "6f85a0b7bbbff23c76d7392514678a61"

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
        document.inference.prediction.supplier_name.value if document.inference.prediction.supplier_name else "Nom Inconnu"
    )
    partner_address = document.inference.prediction.supplier_address.value if document.inference.prediction.supplier_address else "Adresse non fournie"

    line_items = document.inference.prediction.line_items or []
    lines = []

    for item in line_items:
        description = item.description.value if item.description else "Description non fournie"
        unit_price = item.unit_price.value if item.unit_price else 0.0
        quantity = item.quantity.value if item.quantity else 1
        tax_rate = item.tax_rate.value if item.tax_rate else 0.0

        line_data = {
            "description": description,
            "unit_price": unit_price,
            "quantity": quantity,
            "tax_rate": tax_rate,
        }
        lines.append(line_data)

    document_total_net = document.inference.prediction.total_net.value if document.inference.prediction.total_net else 0.0
    document_total_amount = document.inference.prediction.total_amount.value if document.inference.prediction.total_amount else 0.0
    document_total_tax = document.inference.prediction.total_tax.value if document.inference.prediction.total_tax else 0.0

    invoice_data = {
        "partner_name": partner_name,
        "partner_address": partner_address,
        "invoice_date": document.inference.prediction.date.value if document.inference.prediction.date else None,
        "invoice_date_due": document.inference.prediction.due_date.value if document.inference.prediction.due_date else None,
        "invoice_number": document.inference.prediction.invoice_number.value if document.inference.prediction.invoice_number else "Référence inconnue",
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
    pdf_path = "/data/voye/app/Facture_CCL_130616.pdf"  # Chemin de votre fichier PDF
    if os.path.exists(pdf_path):
        extract_and_create_json(pdf_path)
    else:
        _logger.error(f"Le fichier PDF {pdf_path} n'existe pas.")
