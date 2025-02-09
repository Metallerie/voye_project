import requests
import json
import time

# Clé API Mindee
MINDEE_API_KEY = "6f85a0b7bbbff23c76d7392514678a61"

# URLs pour soumettre et récupérer les résultats
SUBMIT_URL = "https://api.mindee.net/v1/products/mindee/invoices/v4/predict"
RESULTS_URL = "https://api.mindee.net/v1/products/mindee/invoices/v4/predict/{job_id}"

# Chemin vers le fichier à soumettre
FILE_PATH = "path/to/your/invoice.pdf"

# En-têtes de la requête
headers = {"Authorization": f"Token {MINDEE_API_KEY}"}

def submit_document(file_path):
    files = {'document': open(file_path, 'rb')}
    response = requests.post(SUBMIT_URL, headers=headers, files=files)
    
    if response.status_code != 201:
        print(f"❌ Erreur lors de la soumission du document : {response.status_code}")
        print(f"🔍 Réponse complète : {response.text}")
        return None

    data = response.json()
    job_id = data.get("job", {}).get("id")
    print(f"📄 Document soumis avec succès. Job ID : {job_id}")
    return job_id

def retrieve_results(job_id):
    while True:
        response = requests.get(RESULTS_URL.format(job_id=job_id), headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Erreur lors de la récupération des résultats : {response.status_code}")
            print(f"🔍 Réponse complète : {response.text}")
            return None

        data = response.json()
        job_status = data.get("document", {}).get("status", "")

        print(f"📊 Statut du job : {job_status}")

        if job_status == "completed":
            print("✅ Résultats récupérés avec succès !")
            return data
        else:
            print("⏳ Traitement en cours... Nouvelle tentative dans 5 secondes.")
            time.sleep(5)

def save_results_to_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    print(f"📁 Résultats enregistrés dans le fichier : {file_path}")

def main():
    # Soumettre le document à Mindee
    job_id = submit_document(FILE_PATH)
    if job_id is not None:
        # Récupérer les résultats de Mindee
        results = retrieve_results(job_id)
        if results is not None:
            # Enregistrer les résultats dans un fichier JSON
            save_results_to_json(results, 'mindee_results.json')

if __name__ == "__main__":
    main()
