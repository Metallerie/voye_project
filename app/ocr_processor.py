import pytesseract
from PIL import Image

class Processor:
    def __init__(self, document_path, api_key=None):
        self.document_path = document_path
    
    def extract_data(self):
        text = pytesseract.image_to_string(Image.open(self.document_path))
        return {"raw_text": text}

