import json
import importlib
import os
import shutil
import sys

class DocumentProcessor:

    def __init__(self, document_path, library_path, supplier_library_path, processed_dir):
        self.document_path = document_path
        self.library_path = library_path
        self.supplier_library_path = supplier_library_path
        self.processed_dir = processed_dir
        self.library = self.load_library()
        self.supplier_library = self.load_supplier_library()
        self.extraction_method = self.determine_extraction_method()
        self.api_key = self.library.get("facture", {}).get("extraction", {}).get("api_key", None)
        self.processor = self.load_processor()
    
    def load_library(self):
        if os.path.exists(self.library_path):
            with open(self.library_path, "r", encoding="utf-8") as file:
                return json.load(file)
        return {}
    
    def load_supplier_library(self):
        if os.path.exists(self.supplier_library_path):
            with open(self.supplier_library_path, "r", encoding="utf-8") as file:
                return json.load(file)
        return {}
    
    def determine_extraction_method(self):
        if self.supplier_library:
            return "OCR"  # Si une bibliothèque fournisseur existe, utiliser OCR
        return "Mindee"  # Sinon, utiliser Mindee
    
    def load_processor(self):
        module_name = f"{self.extraction_method.lower()}_processor"
        module_path = f"{module_name}"
        sys.path.append("/data/voye/app/")  # Ajout du chemin des modules dynamiques
        try:
            module = importlib.import_module(module_path)
            return module.Processor(self.document_path, self.supplier_library, self.api_key)
        except ImportError:
            raise ValueError(f"Module {module_path} non trouvé")
    
    def process(self):
        extracted_data = self.processor.extract_data()
        print("Données brutes extraites :", extracted_data)  # DEB
        structured_data = self.structure_data(extracted_data)
        print("Données structurées :", structured_data)
        self.move_processed_file()
        return structured_data
    
    def structure_data(self, extracted_data):
        structured_data = {"facture": {}}
        for key, value in self.library.get("facture", {}).items():
            if isinstance(value, dict):
                structured_data["facture"][key] = {}
                for sub_key in value.keys():
                    structured_data["facture"][key][sub_key] = extracted_data.get(sub_key, "")
            else:
                structured_data["facture"][key] = extracted_data.get(key, "")
        return structured_data
    
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
        "/data/voye/app/library/facture_library.json", 
        "/data/voye/filestore/partner/library/CCL_supplier_library.json", 
        "/data/voye/processed/"
    )
    processor.process()
