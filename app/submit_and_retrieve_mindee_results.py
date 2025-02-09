import requests
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# Clé API Mindee
MINDEE_API_KEY = "6f85a0b7bbbff23c76d7392514678a61"

# URL pour soumettre et récupérer les résultats
SUBMIT_URL = "https://api.mindee.net/v1/products/mindee/invoices/v4/predict"
RESULTS_URL = "https://api.mindee.net/v1/products/mindee/invoices/v4/predict/{document_id}"

# Chemin vers le fichier à soumettre
FILE_PATH = "/data/voye/app/Facture_CCL_130616.pdf"

# En-têtes de la requête
headers = {"Authorization": f"Token {MINDEE_API_KEY}"}

def submit_document(file_path):
    files = {'document': open(file_path, 'rb')}
    response = requests.post(SUBMIT_URL, headers=headers, files=files)
    
    if response.status_code != 201:
        _logger.error(f"❌ Erreur lors de la soumission du document : {response.status_code}")
        _logger.error(f"🔍 Réponse complète : {response.text}")
        return None

    data = response.json()
    _logger.info(f"🔍 Réponse de l'API après soumission : {json.dumps(data, indent=4, ensure_ascii=False)}")
    
    # Vérification de l'existence de l'identifiant de document dans la réponse
    if "document" in data and "id" in data["document"]:
        document_id = data["document"]["id"]
        _logger.info(f"📄 Document soumis avec succès. Document ID : {document_id}")
        return document_id
    else:
        _logger.error("❌ Impossible de récupérer l'identifiant du document.")
        return None

def retrieve_results(document_id):
    while True:
        response = requests.get(RESULTS_URL.format(document_id=document_id), headers=headers)
        
        if response.status_code != 200:
            _logger.error(f"❌ Erreur lors de la récupération des résultats : {response.status_code}")
            _logger.error(f"🔍 Réponse complète : {response.text}")
            return None

        data = response.json()
        job_status = data.get("document", {}).get("status", "")

        _logger.info(f"📊 Statut du document : {job_status}")

        if job_status == "completed":
            _logger.info("✅ Résultats récupérés avec succès !")
            return data
        else:
            _logger.info("⏳ Traitement en cours... Nouvelle tentative dans 5 secondes.")
            time.sleep(5)

def save_results_to_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    _logger.info(f"📁 Résultats enregistrés dans le fichier : {file_path}")

def process_invoice_data(data):
    document = data.get("document", {})
    inference = document.get("inference", {})
    prediction = inference.get("prediction", {})

    supplier_name = prediction.get("supplier_name", {}).get("value", "Nom Inconnu")
    supplier_address = prediction.get("supplier_address", {}).get("value", "Adresse non fournie")
    invoice_number = prediction.get("invoice_number", {}).get("value", "Référence inconnue")
    invoice_date = prediction.get("date", {}).get("value")
    due_date = prediction.get("due_date", {}).get("value")
    
    line_items = prediction.get("line_items", [])
    total_net = prediction.get("total_net", {}).get("value", 0.0)
    total_amount = prediction.get("total_amount", {}).get("value", 0.0)
    total_tax = prediction.get("total_tax", {}).get("value", 0.0)
    
    _logger.info(f"Fournisseur : {supplier_name}")
    _logger.info(f"Adresse : {supplier_address}")
    _logger.info(f"Numéro de facture : {invoice_number}")
    _logger.info(f"Date de la facture : {invoice_date}")
    _logger.info(f"Date d'échéance : {due_date}")
    _logger.info(f"Total net : {total_net}")
    _logger.info(f"Total montant : {total_amount}")
    _logger.info(f"Total taxe : {total_tax}")

    for item in line_items:
        description = item.get("description", "Description non fournie")
        unit_price = item.get("unit_price", 0.0)
        quantity = item.get("quantity", 1)
        tax_rate = item.get("tax_rate", 0.0)
        total_line = unit_price * quantity
        tax_amount = total_line * (tax_rate / 100.0)
        
        _logger.info(f"Article : {description}")
        _logger.info(f"Prix unitaire : {unit_price}")
        _logger.info(f"Quantité : {quantity}")
        _logger.info(f"Total ligne : {total_line}")
        _logger.info(f"Taxe : {tax_amount}")

def main():
    # Soumettre le document à Mindee
    document_id = submit_document(FILE_PATH)
    if document_id is not None:
        # Récupérer les résultats de Mindee
        results = retrieve_results(document_id)
        if results is not None:
            # Enregistrer les résultats dans un fichier JSON
            save_results_to_json(results, 'mindee_results.json')
            # Traiter les données de la facture
            process_invoice_data(results)

if __name__ == "__main__":
    main()
