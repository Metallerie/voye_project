import json
import importlib
import os
import shutil
import sys
import qrcode
import time

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
    
    def process(self):
        extracted_data = self.processor.extract_data()
        print("Données extraites :", extracted_data)
        self.generate_qr_code(extracted_data)
        self.move_processed_file()
        return extracted_data
    
    def generate_qr_code(self, data):
        if not os.path.exists(self.filestore_dir):
            os.makedirs(self.filestore_dir)
        
        partner_name = data.get("vendeur", "unknown").replace(" ", "_")
        invoice_number = data.get("num_facture", "0000")
        timestamp = str(int(time.time() * 1e6))  # Index temporel précis en microsecondes
        
        qr_data = json.dumps(data, ensure_ascii=False, indent=2)
        qr = qrcode.make(qr_data)
        qr_filename = f"{partner_name}_{invoice_number}_{timestamp}.png"
        qr_path = os.path.join(self.filestore_dir, qr_filename)
        qr.save(qr_path)
        print(f"QR Code enregistré : {qr_path}")
    
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
        "/data/voye/filestore/"
    )
    processor.process()
