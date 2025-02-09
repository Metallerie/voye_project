import os
import requests
import json
import time
import datetime
from pymongo import MongoClient
from mindee import Client, product


# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["voye_db"]

# Fonction pour récupérer un paramètre de voye_config
def get_config(param_key):
    config = db.voye_config.find_one({"key": param_key})
    return config["value"] if config else None

# Récupération des paramètres depuis voye_config
MINDEE_API_KEY = get_config("mindee_api_key")
MINDEE_API_URL = get_config("mindee_api_url")
INVOICE_STORAGE_PATH = get_config("invoice_storage_path")
INPUT_DIRECTORY = get_config("input_directory")  # /data/voye/document/
ARCHIVE_DIRECTORY = get_config("archive_directory")  # /data/voye/archive/{année}

# Vérification des paramètres essentiels
if not all([MINDEE_API_KEY, MINDEE_API_URL, INVOICE_STORAGE_PATH, INPUT_DIRECTORY, ARCHIVE_DIRECTORY]):
    print("❌ Erreur : Certains paramètres sont manquants dans voye_config.")
    exit(1)

# Fonction pour envoyer une facture à Mindee
def send_invoice_to_mindee(file_path):
    headers = {"Authorization": f"Token {MINDEE_API_KEY}"}
    files = {"document": open(file_path, "rb")}
    print(f"📤 Envoi de {file_path} à Mindee...")
    response = requests.post(MINDEE_API_URL, headers=headers, files=files)
    if response.status_code != 201:
        print(f"❌ Erreur API Mindee : {response.status_code}")
        print(f"🔍 Réponse complète : {response.text}")
        return None
    return response.json()

# Fonction pour récupérer les résultats de Mindee
def get_mindee_results(job_id):
    results_url = f"{MINDEE_API_URL}/{job_id}"
    headers = {"Authorization": f"Token {MINDEE_API_KEY}"}
    while True:
        response = requests.get(results_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print("❌ Erreur 404 : Document introuvable")
            return None
        print("⏳ Traitement en cours... Nouvelle tentative dans 5 secondes.")
        time.sleep(5)

# Fonction pour traiter une facture
def process_invoice(file_path):
    file_name = os.path.basename(file_path)
    year = datetime.datetime.now().year
    
    # Envoyer la facture à Mindee
    response_data = send_invoice_to_mindee(file_path)
    if not response_data:
        return
    
    job_id = response_data.get("document", {}).get("id")
    print(f"📊 Job ID reçu : {job_id}")
    
    # Récupérer les résultats
    data = get_mindee_results(job_id)
    if not data:
        return
    
    # Sauvegarde du JSON extrait
    output_dir = os.path.join(INVOICE_STORAGE_PATH, str(year))
    os.makedirs(output_dir, exist_ok=True)
    json_filename = f"invoice_{job_id}.json"
    json_path = os.path.join(output_dir, json_filename)
    
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    
    print(f"✅ Facture extraite et sauvegardée sous {json_path}")
    
    # Indexation dans MongoDB
    db.documents_index.insert_one({
        "original_filename": file_name,
        "document_type": "invoice",
        "stored_filename": json_filename,
        "storage_path": output_dir,
        "timestamp": int(time.time())
    })
    print(f"📌 Index ajouté dans voye_db.documents_index")
    
    # Déplacement du fichier traité vers l'archive
    archive_dir = os.path.join(ARCHIVE_DIRECTORY, str(year))
    os.makedirs(archive_dir, exist_ok=True)
    archived_path = os.path.join(archive_dir, file_name)
    os.rename(file_path, archived_path)
    print(f"📂 Document archivé sous {archived_path}")

# Fonction pour traiter tous les fichiers d'un répertoire
def process_all_invoices():
    if not os.path.exists(INPUT_DIRECTORY):
        print(f"❌ Répertoire d'entrée introuvable : {INPUT_DIRECTORY}")
        return
    
    for file_name in os.listdir(INPUT_DIRECTORY):
        file_path = os.path.join(INPUT_DIRECTORY, file_name)
        if os.path.isfile(file_path):
            process_invoice(file_path)

# Exécution du traitement
if __name__ == "__main__":
    process_all_invoices()
