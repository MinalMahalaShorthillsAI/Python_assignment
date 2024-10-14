from abc import ABC, abstractmethod
import os
from pdfminer.high_level import extract_text
import pdfplumber
from docx import Document
from pptx import Presentation
from pdf2image import convert_from_path
import pytesseract

# Abstract Class for File Loading
class FileLoader(ABC):
    @abstractmethod
    def validate_file(self) -> bool:
        pass

    @abstractmethod
    def load_file(self):
        pass


# Concrete PDFLoader Class
class PDFLoader(FileLoader):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def validate_file(self) -> bool:
        return self.file_path.endswith('.pdf') and os.path.isfile(self.file_path)

    def load_file(self):
        if not self.validate_file():
            raise ValueError("Invalid PDF file")

        # Try to extract text with pdfminer
        try:
            text = extract_text(self.file_path)
            if text.strip():
                return text
            else:
                print("No text found in PDF using pdfminer, falling back to OCR.")
        except Exception as e:
            print(f"Error extracting text with pdfminer: {e}, falling back to OCR.")

        # Fallback to OCR if no text is found
        try:
            return self.extract_text_with_ocr()
        except Exception as e:
            print(f"Error during OCR extraction: {e}")
            raise ValueError("Failed to extract text from PDF.")

    def extract_text_with_ocr(self):
        """Convert PDF pages to images and perform OCR."""
        images = convert_from_path(self.file_path)
        text = ""
        for image in images:
            try:
                ocr_text = pytesseract.image_to_string(image)
                text += ocr_text
            except Exception as e:
                print(f"Error during OCR on one of the pages: {e}")
        return text

    def extract_links(self):
        """Extract hyperlinks from the PDF."""
        links = []
        with pdfplumber.open(self.file_path) as pdf:
            for page in pdf.pages:
                if page.annots:  # Check if annotations are available
                    for annotation in page.annots:
                        if annotation.get("uri"):
                            links.append(annotation["uri"])
        return links

    def extract_images(self):
        """Extract images from the PDF."""
        images = []
        with pdfplumber.open(self.file_path) as pdf:
            for page in pdf.pages:
                if page.images:
                    images.extend(page.images)  # Append images metadata
        return images

    def extract_tables(self):
        """Extract tables from the PDF."""
        tables = []
        with pdfplumber.open(self.file_path) as pdf:
            for page in pdf.pages:
                tables.extend(page.extract_tables())  # Append all tables
        return tables


# Concrete DOCXLoader Class
class DOCXLoader(FileLoader):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = None

    def validate_file(self) -> bool:
        return self.file_path.endswith('.docx') and os.path.isfile(self.file_path)

    def load_file(self):
        if self.validate_file():
            self.content = Document(self.file_path)
            return self.content
        raise ValueError("Invalid DOCX file")


# Concrete PPTLoader Class
class PPTLoader(FileLoader):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = None

    def validate_file(self) -> bool:
        return self.file_path.endswith('.pptx') and os.path.isfile(self.file_path)

    def load_file(self):
        if self.validate_file():
            self.content = Presentation(self.file_path)
            return self.content
        raise ValueError("Invalid PPT file")
