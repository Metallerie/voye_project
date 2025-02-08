import json
import importlib
import os
import shutil
import sys
import time
import re
import asyncio

class DocumentProcessor:

    def __init__(self, document_path, library_path, processed_dir, filestore_dir):
        self.document_path = document_path
        self.library_path = library_path
        self.processed_dir = processed_dir
        self.filestore_dir = filestore_dir
        self.library = self.load_library()
        self.extraction_method = self.determine_extraction_method()
        self.api_key = self.library.get("extraction", {}).get("api_key", None)
        self.processor = self.load_processor()
    
    def load_library(self):
        if os.path.exists(self.library_path):
            with open(self.library_path, "r", encoding="utf-8") as file:
                return json.load(file)
        return {}
    
    def determine_extraction_method(self):
        if self.library:
            return "OCR"  # Si une bibliothèque de référence existe, utiliser OCR
        return "Mindee"  # Sinon, utiliser Mindee
    
    def load_processor(self):
        module_name = f"{self.extraction_method.lower()}_processor"
        module_path = f"{module_name}"
        sys.path.append("/data/voye/app/")  # Ajout du chemin des modules dynamiques
        try:
            module = importlib.import_module(module_path)
            return module.Processor(self.document_path)
        except ImportError:
            raise ValueError(f"Module {module_path} non trouvé")
    
    async def process(self):
        extracted_data = self.processor.extract_data()
        if asyncio.iscoroutine(extracted_data):
            extracted_data = await extracted_data
        print("Données extraites :", json.dumps(extracted_data, indent=4, ensure_ascii=False))
        
        # Stocker toutes les données extraites dans le fichier JSON
        self.store_json_data(extracted_data)
        self.move_processed_file()
        return extracted_data
    
    def store_json_data(self, data):
        if not os.path.exists(self.filestore_dir):
            os.makedirs(self.filestore_dir)
        
        partner_name = data.get("fournisseur", "unknown").replace(" ", "_").replace("/", "_")
        document_number = data.get("num_facture", "0000").replace("/", "_")
        timestamp = str(int(time.time() * 1e6))  # Index temporel précis en microsecondes
        
        json_filename = f"{partner_name}_{document_number}_{timestamp}.json"
        json_path = os.path.join(self.filestore_dir, json_filename)
        
        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        
        print(f"Fichier JSON enregistré : {json_path}")
    
    def move_processed_file(self):
        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)
        dest_path = os.path.join(self.processed_dir, os.path.basename(self.document_path))
        shutil.move(self.document_path, dest_path)
        print(f"Fichier déplacé vers {dest_path}")
    
# Exemple d'utilisation
if __name__ == "__main__":
    print("🚀 Démarrage du traitement du document...")
    processor = DocumentProcessor(
        "/data/voye/document/Facture_CCL_130616.pdf", 
        "/data/voye/filestore/partner/library/CCL_supplier_library.json", 
        "/data/voye/processed/",
        "/data/voye/filestore/account/factures/2025/"
    )
    asyncio.run(processor.process())
