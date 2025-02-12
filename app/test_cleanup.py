import os
import shutil
import logging
from pymongo import MongoClient

# Configuration du logger
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["voye_db"]
index_collection = db["index_document"]

# Chemins des répertoires
invoice_path = "/data
