import requests
import json

# Clé API Mindee
MINDEE_API_KEY = "6f85a0b7bbbff23c76d7392514678a61"

# URL d'upload (vérifiée avec curl)
UPLOAD_URL = "https://api.mindee.net/v1/products/mindee/invoices/v4/predict"

# 📤 Envoi du fichier
headers = {"Authorization": f"Token {MINDEE_API_KEY}"}
files = {"document": open("Facture_CCL_130616.pdf", "rb")}

print("📤 Envoi du document à Mindee...")
response = requests.post(UPLOAD_URL, headers=headers, files=files)

# 🔍 Vérification de la réponse
if response.status_code != 201:
    print(f"❌ Erreur API Mindee : {response.status_code}")
    print(f"🔍 Réponse complète : {response.text}")
else:
    data = response.json()
    print("✅ Réponse reçue avec succès !")
    print(json.dumps(data, indent=4, ensure_ascii=False))

    # Récupération du Job ID
    job_id = data.get("document", {}).get("id")
    print(f"📊 Job ID : {job_id}")
