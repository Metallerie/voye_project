import os
import json
import datetime
import subprocess
from pymongo import MongoClient

# Configuration
MONGO_HOST = "localhost"
MONGO_PORT = "27017"
DB_NAME = "voye_db"
BACKUP_DIR = "/data/voye/mongo_backups"
GIT_REPO_PATH = "/data/voye/app/voye_project"
GIT_REMOTE_URL = "git@github.com:Metallerie/voye_project.git"

# Assurer l'existence du dossier
os.makedirs(BACKUP_DIR, exist_ok=True)

# Générer le nom du fichier JSON avec la date
date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_file = os.path.join(BACKUP_DIR, f"backup_{DB_NAME}_{date_str}.json")

print(f"🔄 Sauvegarde MongoDB en JSON... ({backup_file})")

# Connexion à MongoDB et export en JSON
with MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}/") as client:
    db = client[DB_NAME]
    backup_data = {collection: list(db[collection].find({}, {"_id": 0})) for collection in db.list_collection_names()}

# Enregistrer dans un fichier JSON
with open(backup_file, "w", encoding="utf-8") as f:
    json.dump(backup_data, f, indent=4, ensure_ascii=False)

print(f"✅ Sauvegarde terminée : {backup_file}")

# Copier le fichier JSON dans le dépôt Git
backup_git_file = os.path.join(GIT_REPO_PATH, f"backup_{DB_NAME}_{date_str}.json")
os.rename(backup_file, backup_git_file)

# Vérifier si le dépôt Git est bien initialisé
if not os.path.exists(os.path.join(GIT_REPO_PATH, ".git")):
    subprocess.run(["git", "init"], cwd=GIT_REPO_PATH)
    subprocess.run(["git", "remote", "add", "origin", GIT_REMOTE_URL], cwd=GIT_REPO_PATH)

# Ajouter et pousser la sauvegarde sur GitHub
try:
    subprocess.run(["git", "add", "."], cwd=GIT_REPO_PATH)
    subprocess.run(["git", "commit", "-m", f"Backup JSON MongoDB {DB_NAME} {date_str}"], cwd=GIT_REPO_PATH)
    subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=GIT_REPO_PATH)  # Synchroniser avant push
    subprocess.run(["git", "push", "origin", "main"], cwd=GIT_REPO_PATH)
    print("✅ Sauvegarde poussée sur Git ✅")
except subprocess.CalledProcessError as e:
    print(f"❌ Erreur lors du push sur Git : {e}")
