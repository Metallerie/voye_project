import os
import requests
import json
import datetime
import time
from pymongo import MongoClient

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
MINDEE_STATUS_URL = get_config("url_status")
INVOICE_STORAGE_PATH = get_config("invoice_storage_path")
INPUT_DIRECTORY = get_config("input_directory")  # /data/voye/document/
ARCHIVE_DIRECTORY = get_config("archive_directory")  # /data/voye/archive/{année}

# Vérification des paramètres essentiels
if not all([MINDEE_API_KEY, MINDEE_API_URL, MINDEE_STATUS_URL, INVOICE_STORAGE_PATH, INPUT_DIRECTORY, ARCHIVE_DIRECTORY]):
    print("❌ Erreur : Certains paramètres sont manquants dans voye_config.")
    exit(1)

# Fonction pour vérifier le statut d'une requête Mindee
def get_mindee_results(job_id, response_data):
    # Utilisation de l'URL correcte pour récupérer les résultats
    status_url = MINDEE_STATUS_URL.format(job_id=job_id)
    
    headers = {"Authorization": f"Token {MINDEE_API_KEY}"}
    
    while True:
        response = requests.get(status_url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Erreur lors de la récupération des résultats : {response.status_code}")
            try:
                error_details = response.json()
                print("🔍 Détails de l'erreur :", json.dumps(error_details, indent=4))
            except json.JSONDecodeError:
                print("🔍 Impossible de décoder la réponse JSON de l'erreur.")
            return None
        
        data = response.json()
        if data.get("job", {}).get("status") == "completed":
            return data
        
        print("⏳ Traitement en cours... Attente de 5 secondes.")
        time.sleep(5)

# Fonction pour traiter une facture avec Mindee
def process_invoice(file_path):
    file_name = os.path.basename(file_path)
    year = datetime.datetime.now().year
    
    # Vérifier si le fichier est déjà indexé
    existing = db.documents_index.find_one({"original_filename": file_name})
    if existing:
        print(f"⚠️ Le fichier {file_name} existe déjà dans l'index. Ignoré.")
        return
    
    # Préparation de la requête API
    headers = {"Authorization": f"Token {MINDEE_API_KEY}"}
    files = {"document": open(file_path, "rb")}
    
    print(f"📤 Envoi de {file_name} à Mindee...")
    response = requests.post(MINDEE_API_URL, headers=headers, files=files)
    
    if response.status_code != 201:
        print(f"❌ Erreur API Mindee : {response.status_code}")
        print(f"🔍 Réponse complète : {response.text}")  # Ajout pour debug
        return
    
    response_data = response.json()
    print("🔍 Réponse complète de Mindee :", json.dumps(response_data, indent=4))  # Debug
    
    job_id = response_data.get("document", {}).get("id")
    print(f"📊 Job ID reçu : {job_id}. Attente des résultats...")
    data = get_mindee_results(job_id, response_data)
    if not data:
        return
    
    # Création du dossier de stockage
    output_dir = os.path.join(INVOICE_STORAGE_PATH, str(year))
    os.makedirs(output_dir, exist_ok=True)
    
    # Nom du fichier JSON stocké
    timestamp = int(datetime.datetime.now().timestamp())
    supplier_name = "unknown_supplier"  # À améliorer plus tard
    json_filename = f"{supplier_name}_invoice_{timestamp}.json"
    json_path = os.path.join(output_dir, json_filename)
    
    # Sauvegarde du JSON extrait
    with open(json_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
    
    print(f"✅ Facture extraite et sauvegardée sous {json_path}")
    
    # Indexation dans MongoDB
    db.documents_index.insert_one({
        "original_filename": file_name,
        "document_type": "invoice",
        "stored_filename": json_filename,
        "storage_path": output_dir,
        "supplier_name": supplier_name,
        "timestamp": timestamp
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
