import requests
import json
import time

# Clé API Mindee
MINDEE_API_KEY = "6f85a0b7bbbff23c76d7392514678a61"

# URL pour soumettre et récupérer les résultats
SUBMIT_URL = "https://api.mindee.net/v1/products/mindee/invoices/v4/predict"
RESULTS_URL = "https://api.mindee.net/v1/products/mindee/invoices/v4/documents/{document_id}"

# Chemin vers le fichier à soumettre
FILE_PATH = "/data/voye/app/Facture_CCL_130616.pdf"

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
    print(f"🔍 Réponse de l'API après soumission : {json.dumps(data, indent=4, ensure_ascii=False)}")
    
    # Vérification de l'existence de l'identifiant de document dans la réponse
    if "document" in data and "id" in data["document"]:
        document_id = data["document"]["id"]
        print(f"📄 Document soumis avec succès. Document ID : {document_id}")
        return document_id
    else:
        print("❌ Impossible de récupérer l'identifiant du document.")
        return None

def retrieve_results(document_id):
    while True:
        response = requests.get(RESULTS_URL.format(document_id=document_id), headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Erreur lors de la récupération des résultats : {response.status_code}")
            print(f"🔍 Réponse complète : {response.text}")
            return None

        data = response.json()
        job_status = data.get("document", {}).get("status", "")

        print(f"📊 Statut du document : {job_status}")

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
    document_id = submit_document(FILE_PATH)
    if document_id is not None:
        # Récupérer les résultats de Mindee
        results = retrieve_results(document_id)
        if results is not None:
            # Enregistrer les résultats dans un fichier JSON
            save_results_to_json(results, 'mindee_results.json')

if __name__ == "__main__":
    main()
