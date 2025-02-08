import json
import importlib
import os
import shutil
import sys
import time
import re

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
            return module.Processor(self.document_path, self.api_key)
        except ImportError:
            raise ValueError(f"Module {module_path} non trouvé")
    
    def extract_invoice_number(self, text):
        match = re.search(r'FACTURE N°[:\s]+(\d+)', text, re.IGNORECASE)
        return match.group(1) if match else "0000"
    
    def extract_vendor_name(self, text):
        match = re.search(r'Comptoir Commercial du Languedoc', text, re.IGNORECASE)
        return "CCL" if match else "unknown"
    
    def extract_total_amount(self, text):
        match = re.search(r'NET A PAYER\s+(\d+[,.]\d+)', text, re.IGNORECASE)
        return match.group(1) if match else "0.00"
    
    def extract_articles(self, text):
        articles = []
        matches = re.findall(r'(\d{5,})\s+([A-Z0-9\s]+)\s+(\d+[,.]\d+)\s+\S+\s+(\d+[,.]\d+)\s+(\d+[,.]\d+)', text)
        for match in matches:
            articles.append({
                "reference": match[0],
                "designation": match[1].strip(),
                "quantite": float(match[2].replace(',', '.')),
                "prix_unitaire": float(match[3].replace(',', '.')),
                "montant": float(match[4].replace(',', '.'))
            })
        return articles
    
    def process(self):
        extracted_data = self.processor.extract_data()
        print("Données extraites :", extracted_data)
        
        extracted_text = extracted_data.get("text", "")
        structured_data = {
            "vendeur": self.extract_vendor_name(extracted_text),
            "num_facture": self.extract_invoice_number(extracted_text),
            "total_net_a_payer": self.extract_total_amount(extracted_text),
            "articles": self.extract_articles(extracted_text)
        }
        
        self.store_json_data(structured_data)
        self.move_processed_file()
        return structured_data
    
    def store_json_data(self, data):
        if not os.path.exists(self.filestore_dir):
            os.makedirs(self.filestore_dir)
        
        partner_name = data.get("vendeur", "unknown").replace(" ", "_").replace("/", "_")
        invoice_number = data.get("num_facture", "0000").replace("/", "_")
        timestamp = str(int(time.time() * 1e6))  # Index temporel précis en microsecondes
        
        json_filename = f"{partner_name}_{invoice_number}_{timestamp}.json"
        json_path = os.path.join(self.filestore_dir, json_filename)
        
        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=2)
        
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
    processor.process()
