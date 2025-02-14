import os
import subprocess
import datetime
import shutil
from pymongo import MongoClient

# Récupérer la configuration depuis MongoDB
def get_config():
    with MongoClient("mongodb://localhost:27017/") as client:
        db = client["voye_db"]
        collection = db["voye_config"]
        return {item["key"]: item["value"] for item in collection.find()}

# Charger la configuration
config = get_config()

# Configuration par défaut + récupérée de MongoDB
MONGO_HOST = config.get("MONGO_HOST", "localhost")
MONGO_PORT = config.get("MONGO_PORT", "27017")
DB_NAME = config.get("DB_NAME", "voye_db")  # Nom de la base MongoDB
BACKUP_DIR = config.get("BACKUP_DIR", "/data/voye/mongo_backups")  # Dossier local des backups
GIT_REPO_PATH = config.get("GIT_REPO_PATH", "/voye_project/mongo_backups")  # Chemin du dépôt Git
GIT_REMOTE_URL = "git@github.com:Metallerie/voye_project.git"  # URL du repo Git
RETENTION_DAYS = int(config.get("RETENTION_DAYS", 7))  # Durée de rétention des backups

# Assurer l'existence des dossiers
os.makedirs(BACKUP_DIR, exist_ok=True)
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

# Copier le dump vers le dépôt Git
backup_git_path = os.path.join(GIT_REPO_PATH, f"mongo_backup_{DB_NAME}_{date_str}")
shutil.move(backup_path, backup_git_path)

# Initialiser le dépôt Git s'il n'existe pas encore
if not os.path.exists(os.path.join(GIT_REPO_PATH, ".git")):
    subprocess.run(["git", "init"], cwd=GIT_REPO_PATH)
    subprocess.run(["git", "remote", "add", "origin", GIT_REMOTE_URL], cwd=GIT_REPO_PATH)

# Ajouter, committer et pousser vers Git
try:
    subprocess.run(["git", "add", "."], cwd=GIT_REPO_PATH)
    subprocess.run(["git", "commit", "-m", f"Backup MongoDB {DB_NAME} {date_str}"], cwd=GIT_REPO_PATH)
    subprocess.run(["git", "push", "origin", "main"], cwd=GIT_REPO_PATH)
    print("✅ Sauvegarde poussée sur Git ✅")
except subprocess.CalledProcessError as e:
    print(f"❌ Erreur lors du push sur Git : {e}")
    exit(1)

# Suppression des anciennes sauvegardes locales
now = datetime.datetime.now()
for folder in os.listdir(BACKUP_DIR):
    folder_path = os.path.join(BACKUP_DIR, folder)
    if os.path.isdir(folder_path):
        try:
            folder_time = datetime.datetime.strptime(folder.split("_")[-1], "%Y-%m-%d_%H-%M-%S")
            age_days = (now - folder_time).days
            if age_days > RETENTION_DAYS:
                shutil.rmtree(folder_path)
                print(f"🗑 Ancienne sauvegarde supprimée : {folder_path} (Âgée de {age_days} jours)")
        except ValueError:
            continue  # Ignore les dossiers mal formatés

print("✅ Nettoyage terminé.")
