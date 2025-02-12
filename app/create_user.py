import os
import json
import datetime
import hashlib
from pymongo import MongoClient

# Configuration des chemins
USER_DIR = "/data/voye/filestore/user/"
os.makedirs(USER_DIR, exist_ok=True)

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["voye_db"]
index_collection = db["index_document"]
config_collection = db["voye_frontend_config"]

def generate_user(user_id, name, email, role="user"):
    # Générer un timestamp
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    # Générer un hash basé sur user_id + email
    user_hash = hashlib.md5(f"{user_id}{email}".encode()).hexdigest()[:8]

    # Définir le nom de fichier
    filename = f"{timestamp}_{user_hash}.json"
    user_file = os.path.join(USER_DIR, filename)

    # Vérifier si l'utilisateur existe déjà dans `index_document`
    existing_user = index_collection.find_one({"user_id": user_id})
    if existing_user:
        print(f"⚠️ L'utilisateur {user_id} existe déjà.")
        return

    # Création du profil utilisateur
    user_data = {
        "user_id": user_id,
        "name": name,
        "email": email,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "role": role
    }

    # Écriture du fichier JSON
    with open(user_file, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

    print(f"✅ Fichier utilisateur créé : {user_file}")

    # Calculer un hash du fichier
    file_hash = hashlib.md5(json.dumps(user_data, sort_keys=True).encode()).hexdigest()

    # Ajout dans `index_document` (respect du format des factures)
    document_index = {
        "document_type": "User",
        "filename": filename,
        "storage_path": user_file,
        "user_id": user_id,
        "name": name,
        "email": email,
        "file_hash": file_hash,
        "timestamp": datetime.datetime.utcnow()
    }
    index_collection.insert_one(document_index)
    print(f"✅ Utilisateur indexé dans `index_document`")

    # Ajout dans `voye_frontend_config` (respect du format des factures)
    user_config = {
        "user_id": user_id,
        "theme": "light",
        "layout": "right-handed",
        "language": "fr",
        "buttons_size": "large",
        "show_tutorial": True
    }
    config_collection.insert_one(user_config)
    print(f"✅ Configuration frontend ajoutée pour {user_id}")

if __name__ == "__main__":
    generate_user("admin", "Administrateur", "admin@voye.local", "admin")
