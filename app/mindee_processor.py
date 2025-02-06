import requests

class Processor:
    def __init__(self, document_path, api_key):
        self.document_path = document_path
        self.api_key = api_key
    
    def extract_data(self):
        if not self.api_key:
            raise ValueError("Clé API Mindee non fournie")
        
        url = "https://api.mindee.net/v1/products/mindee/invoices/v4/predict"
        headers = {"Authorization": f"Token {self.api_key}"}
        files = {"document": open(self.document_path, "rb")}
        
        response = requests.post(url, headers=headers, files=files)
        return response.json()
