from fastapi import FastAPI
from pymongo import MongoClient

app = FastAPI()

# Connexion à MongoDB
MONGO_URI = "mongodb://voye_user:password_secure@89.47.51.175:27017/voye"
client = MongoClient(MONGO_URI)
db = client["voye"]

@app.get("/")
def read_root():
    return {"message": "API FastAPI connectée à MongoDB avec succès !"}

@app.get("/documents/")
def get_documents():
    documents = list(db.documents.find({}, {"_id": 0}))  # Exclure _id pour éviter l'erreur JSON
    return {"documents": documents}

@app.post("/documents/")
def add_document(data: dict):
    db.documents.insert_one(data)
    return {"message": "Document ajouté avec succès!"}
