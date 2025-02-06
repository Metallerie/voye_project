from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import os

class Processor:
    def __init__(self, document_path, api_key=None):
        self.document_path = document_path

    def extract_data(self):
        # Vérifie si le fichier est un PDF et le convertit en images
        if self.document_path.lower().endswith(".pdf"):
            images = convert_from_path(self.document_path)
            text = ""
            for i, img in enumerate(images):
                text += pytesseract.image_to_string(img) + "\n"
        else:
            text = pytesseract.image_to_string(Image.open(self.document_path))

        return {"text": text}

