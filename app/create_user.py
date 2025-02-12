import os
import json
import datetime
import hashlib
from pymongo import MongoClient

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["voye_db"]
index_collection = db["index_document"]
config_collection = db["voye_frontend_config"]
config_data = db["voye_config"].find_one({"key": "user_directory"})

# Vérification de la config
if not config_data:
    raise Exception("❌ ERREUR: L'entrée 'user_directory' est manquante dans voye_config.")

USER_DIR = config_data["value"]
os.makedirs(USER_DIR, exist_ok=True)  # Création du répertoire s'il n'existe pas


def generate_user(user_id, name, email, role="user"):
    """Crée un nouvel utilisateur avec un fichier JSON et une entrée MongoDB."""
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    user_hash = hashlib.md5(f"{user_id}{email}".encode()).hexdigest()[:8]
    filename = f"{timestamp}_{user_hash}.json"
    user_file = os.path.join(USER_DIR, filename)

    # Vérifier si l'utilisateur existe déjà
    existing_user = index_collection.find_one({"user_id": user_id})
    if existing_user:
        print(f"⚠️ L'utilisateur {user_id} existe déjà.")
        return

    user_data = {
        "user_id": user_id,
        "name": name,
        "email": email,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "role": role
    }

    with open(user_file, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

    print(f"✅ Fichier utilisateur créé : {user_file}")

    checksum = hashlib.md5(json.dumps(user_data, sort_keys=True).encode()).hexdigest()

    document_index = {
        "document_type": "User",
        "filename": filename,
        "storage_path": user_file,
        "user_id": user_id,
        "name": name,
        "email": email,
        "checksum": checksum,
        "timestamp": datetime.datetime.utcnow()
    }
    index_collection.insert_one(document_index)
    config_collection.insert_one({"user_id": user_id, "theme": "light", "layout": "right-handed",
                                  "language": "fr", "buttons_size": "large", "show_tutorial": True})

    print(f"✅ Utilisateur {user_id} ajouté avec succès.")


def update_user(user_id, **kwargs):
    """Modifie un utilisateur en mettant à jour son fichier JSON et MongoDB."""
    existing_user = index_collection.find_one({"user_id": user_id})
    if not existing_user:
        print(f"❌ L'utilisateur {user_id} n'existe pas.")
        return

    user_file = existing_user["storage_path"]

    if not os.path.exists(user_file):
        print(f"❌ Fichier utilisateur introuvable : {user_file}")
        return

    with open(user_file, "r", encoding="utf-8") as f:
        user_data = json.load(f)

    for key, value in kwargs.items():
        if value is not None:
            user_data[key] = value

    with open(user_file, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=4)

    checksum = hashlib.md5(json.dumps(user_data, sort_keys=True).encode()).hexdigest()

    index_collection.update_one(
        {"user_id": user_id},
        {"$set": {**kwargs, "checksum": checksum, "timestamp": datetime.datetime.utcnow()}}
    )

    print(f"✅ Utilisateur {user_id} mis à jour avec succès.")


def delete_user(user_id):
    """Supprime un utilisateur (JSON + entrée MongoDB)."""
    existing_user = index_collection.find_one({"user_id": user_id})
    if not existing_user:
        print(f"❌ L'utilisateur {user_id} n'existe pas.")
        return

    user_file = existing_user["storage_path"]

    if os.path.exists(user_file):
        os.remove(user_file)
        print(f"🗑️ Fichier utilisateur supprimé : {user_file}")

    index_collection.delete_one({"user_id": user_id})
    config_collection.delete_one({"user_id": user_id})

    print(f"✅ Utilisateur {user_id} supprimé avec succès.")


if __name__ == "__main__":
    action = input("Que voulez-vous faire ? (ajouter/modifier/supprimer) : ").strip().lower()

    if action == "ajouter":
        user_id = input("User ID : ")
        name = input("Nom : ")
        email = input("Email : ")
        role = input("Rôle (admin/user) : ") or "user"
        generate_user(user_id, name, email, role)

    elif action == "modifier":
        user_id = input("User ID de l'utilisateur à modifier : ")
        new_name = input("Nouveau nom (laisser vide si inchangé) : ") or None
        new_email = input("Nouvel email (laisser vide si inchangé) : ") or None
        update_user(user_id, name=new_name, email=new_email)

    elif action == "supprimer":
        user_id = input("User ID de l'utilisateur à supprimer : ")
        confirm = input(f"⚠️ Confirmer la suppression de {user_id} ? (oui/non) : ")
        if confirm.lower() == "oui":
            delete_user(user_id)

    else:
        print("❌ Action invalide.")
