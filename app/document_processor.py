import json
import importlib
import os
import shutil
import sys

class DocumentProcessor:

    def __init__(self, document_path, library_dir, processed_dir):
        self.document_path = document_path
        self.library_dir = library_dir
        self.processed_dir = processed_dir
        self.supplier_library = self.load_supplier_library()
        self.extraction_method = self.determine_extraction_method()
        self.api_key = self.supplier_library.get("extraction", {}).get("api_key", None)
        self.processor = self.load_processor()
    
    def load_supplier_library(self):
        supplier_name = self.identify_supplier()
        supplier_library_path = os.path.join(self.library_dir, f"{supplier_name}_supplier_library.json")
        if os.path.exists(supplier_library_path):
            with open(supplier_library_path, "r", encoding="utf-8") as file:
                return json.load(file)
        return {}
    
    def identify_supplier(self):
        # Placeholder logic to determine supplier based on document content
        return "CCL"
    
    def determine_extraction_method(self):
        if self.supplier_library:
            return "OCR"  # Utilisation de la bibliothèque fournisseur avec OCR
        return "Mindee"  # Utilisation de Mindee si aucune bibliothèque n'est disponible
    
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
        structured_data = self.structure_extracted_data(extracted_data)
        print("Données structurées :", structured_data)
        self.move_processed_file()
        return structured_data
    
    def structure_extracted_data(self, extracted_data):
        # Implémenter la transformation des données extraites selon la bibliothèque fournisseur
        structured_data = {
            "facture": {
                "identification": {
                    "vendeur": extracted_data.get("supplier_name", ""),
                    "client": extracted_data.get("customer_name", "")
                },
                "references": {
                    "numero_facture": extracted_data.get("invoice_number", ""),
                    "date_emission": extracted_data.get("date", ""),
                    "date_echeance": ""
                },
                "totaux": {
                    "total_HT": extracted_data.get("total_net", ""),
                    "total_TVA": extracted_data.get("total_tax", ""),
                    "total_TTC": extracted_data.get("total_amount", "")
                },
                "paiement": {
                    "IBAN": extracted_data.get("supplier_payment_details", {}).get("iban", ""),
                    "BIC": extracted_data.get("supplier_payment_details", {}).get("swift", "")
                }
            }
        }
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
        "/data/voye/filestore/partner/library/", 
        "/data/voye/processed/"
    )
    processor.process()
