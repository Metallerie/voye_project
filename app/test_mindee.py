import requests
import time
import json

# Clé API Mindee (à récupérer dans voye_config ou à renseigner manuellement)
MINDEE_API_KEY = "TA_CLE_API_MINDEE_ICI"
MINDEE_API_URL = "https://api.mindee.net/v1/products/mindee/invoices/v4/predict"
MINDEE_STATUS_URL = "https://api.mindee.net/v1/products/mindee/invoices/v4/documents/queue/{job_id}"

# Chemin du fichier de test
TEST_FILE_PATH = "Facture_CCL_130616.pdf"

def send_to_mindee(file_path):
    """ Envoie un fichier à Mindee et retourne le job_id. """
    headers = {"Authorization": f"Token {MINDEE_API_KEY}"}
    files = {"document": open(file_path, "rb")}

    print("📤 Envoi du document à Mindee...")
    response = requests.post(MINDEE_API_URL, headers=headers, files=files)
    
    if response.status_code != 201:
        print(f"❌ Erreur API Mindee : {response.status_code}")
        print(f"🔍 Réponse complète : {response.text}")
        return None
    
    response_data = response.json()
    print("✅ Réponse API reçue :", json.dumps(response_data, indent=4))

    job_id = response_data.get("document", {}).get("id")
    if not job_id:
        print("⚠️ Impossible de récupérer le Job ID")
        return None
    
    print(f"📊 Job ID reçu : {job_id}")
    return job_id

def check_status(job_id):
    """ Vérifie le statut du traitement et récupère les résultats. """
    status_url = MINDEE_STATUS_URL.format(job_id=job_id)
    headers = {"Authorization": f"Token {MINDEE_API_KEY}"}

    while True:
        response = requests.get(status_url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Erreur lors de la récupération des résultats : {response.status_code}")
            print(f"🔍 Réponse complète : {response.text}")
            return None

        data = response.json()
        print("🔍 Statut du traitement :", json.dumps(data, indent=4))

        job_status = data.get("job", {}).get("status", "unknown")
        if job_status == "completed":
            print("✅ Traitement terminé, résultats disponibles.")
            return data
        elif job_status == "failed":
            print("❌ Le traitement a échoué.")
            return None

        print("⏳ En attente de Mindee... (pause de 5 sec)")
        time.sleep(5)

if __name__ == "__main__":
    job_id = send_to_mindee(TEST_FILE_PATH)
    if job_id:
        results = check_status(job_id)
        if results:
            print("✅ Données extraites :", json.dumps(results, indent=4))
        else:
            print("⚠️ Aucune donnée récupérée.")

