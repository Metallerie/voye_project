import requests
import json
import time

# Clé API Mindee
MINDEE_API_KEY = "6f85a0b7bbbff23c76d7392514678a61"

# URL de récupération des résultats (VÉRIFIÉE AVEC LA DOC)
RESULTS_URL = "https://api.mindee.net/v1/products/mindee/invoices/v4/documents/queue/{job_id}"

# Remplace par ton Job ID reçu
job_id = "b6123ff8-f290-405b-b4c5-3ded2539c593"

# 📤 Envoi de la requête pour récupérer les résultats
headers = {"Authorization": f"Token {MINDEE_API_KEY}"}

while True:
    response = requests.get(RESULTS_URL.format(job_id=job_id), headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Erreur lors de la récupération des résultats : {response.status_code}")
        print(f"🔍 Réponse complète : {response.text}")
        break

    data = response.json()
    job_status = data.get("job", {}).get("status", "")

    print(f"📊 Statut du job : {job_status}")

    if job_status == "completed":
        print("✅ Résultats récupérés avec succès !")
        print(json.dumps(data, indent=4, ensure_ascii=False))
        break
    else:
        print("⏳ Traitement en cours... Nouvelle tentative dans 5 secondes.")
        time.sleep(5)
