import os
import subprocess
import datetime
import shutil
from pymongo import MongoClient

# Fonction pour récupérer la config depuis MongoDB
def get_config():
    with MongoClient("mongodb://localhost:27017/") as client:
        db = client["voye_db"]
        collection = db["voye_config"]
        return {item["key"]: item["value"] for item in collection.find()}

# Charger la configuration
config = get_config()

# Configuration locale et GitHub
MONGO_HOST = config.get("MONGO_HOST", "localhost")
MONGO_PORT = config.get("MONGO_PORT", "27017")
DB_NAME = config.get("DB_NAME", "voye_db")
BACKUP_DIR = config.get("BACKUP_DIR", "/data/voye/mongo_backups")  # Assure-toi que ce dossier est accessible
GIT_REPO_PATH = config.get("GIT_REPO_PATH", "/data/voye/mongo_backups/")  # Chemin où est cloné le dépôt Git
GIT_REMOTE_URL = "git@github.com:Metallerie/voye_project.git"
RETENTION_DAYS = int(config.get("RETENTION_DAYS", 7))

# ✅ Vérifier si le chemin GIT_REPO_PATH est bien défini AVANT son utilisation
if not GIT_REPO_PATH:
    raise ValueError("⚠️ Erreur : GIT_REPO_PATH n'est pas défini ! Vérifie la configuration.")

# ✅ S'assurer que le dossier existe
os.makedirs(GIT_REPO_PATH, exist_ok=True)

# Générer un nom de dossier avec la date
date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_path = os.path.join(BACKUP_DIR, f"mongo_backup_{DB_NAME}_{date_str}")

print(f"🔄 Démarrage de la sauvegarde MongoDB... ({backup_path})")

# Exécuter mongodump
dump_cmd = [
    "mongodump",
    f"--host={MONGO_HOST}",
    f"--port={MONGO_PORT}",
    f"--db={DB_NAME}",
    f"--out={backup_path}"
]

try:
    subprocess.run(dump_cmd, check=True)
    print(f"✅ Sauvegarde terminée : {backup_path}")
except subprocess.CalledProcessError as e:
    print(f"❌ Erreur lors de la sauvegarde : {e}")
    exit(1)

# Copier le dump dans le dépôt Git
backup_git_path = os.path.join(GIT_REPO_PATH, f"mongo_backup_{DB_NAME}_{date_str}")
shutil.move(backup_path, backup_git_path)

# Initialiser le dépôt Git s'il n'existe pas encore
if not os.path.exists(os.path.join(GIT_REPO_PATH, ".git")):
    subprocess.run(["git", "init"], cwd=GIT_REPO_PATH)
    subprocess.run(["git", "remote", "add", "origin", GIT_REMOTE_URL], cwd=GIT_REPO_PATH)

# Vérifier si la branche "main" existe, sinon la créer
subprocess.run(["git", "branch", "-M", "main"], cwd=GIT_REPO_PATH)

# Ajouter, committer et pousser sur GitHub
try:
    subprocess.run(["git", "add", "."], cwd=GIT_REPO_PATH)
    subprocess.run(["git", "commit", "-m", f"Backup MongoDB {DB_NAME} {date_str}"], cwd=GIT_REPO_PATH)
    subprocess.run(["git", "push", "origin", "main"], cwd=GIT_REPO_PATH)
    print("✅ Sauvegarde poussée sur Git ✅")
except subprocess.CalledProcessError as e:
    print(f"❌ Erreur lors du push sur Git : {e}")
    exit(1)
