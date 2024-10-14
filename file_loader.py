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
    """Abstract base class for loading different file types."""
    
    @abstractmethod
    def validate_file(self) -> bool:
        """Check if the file is valid."""
        pass

    @abstractmethod
    def load_file(self):
        """Load the file and return its content."""
        pass


# Concrete PDFLoader Class
class PDFLoader(FileLoader):
    """Concrete implementation of FileLoader for PDF files."""
    
    def __init__(self, file_path: str):
        """
        Initialize the PDFLoader with the path to a PDF file.

        Args:
            file_path (str): The path to the PDF file.
        """
        self.file_path = file_path

    def validate_file(self) -> bool:
        """Validate if the file is a PDF and exists."""
        return self.file_path.endswith('.pdf') and os.path.isfile(self.file_path)

    def load_file(self):
        """
        Load the PDF file and extract text.

        Returns:
            str: Extracted text from the PDF.

        Raises:
            ValueError: If the PDF file is invalid or if text extraction fails.
        """
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
        """Convert PDF pages to images and perform OCR to extract text.

        Returns:
            str: Extracted text from the PDF images.
        """
        images = convert_from_path(self.file_path)  # Convert PDF pages to images
        text = ""
        for image in images:
            try:
                ocr_text = pytesseract.image_to_string(image)  # Use OCR to extract text from each image
                text += ocr_text
            except Exception as e:
                print(f"Error during OCR on one of the pages: {e}")
        return text

    def extract_links(self):
        """Extract hyperlinks from the PDF.

        Returns:
            list: A list of hyperlinks found in the PDF.
        """
        links = []
        with pdfplumber.open(self.file_path) as pdf:
            for page in pdf.pages:
                if page.annots:  # Check if annotations are available
                    for annotation in page.annots:
                        if annotation.get("uri"):
                            links.append(annotation["uri"])  # Append the hyperlink
        return links

    def extract_images(self):
        """Extract images from the PDF.

        Returns:
            list: A list of image metadata found in the PDF.
        """
        images = []
        with pdfplumber.open(self.file_path) as pdf:
            for page in pdf.pages:
                if page.images:
                    images.extend(page.images)  # Append images metadata
        return images

    def extract_tables(self):
        """Extract tables from the PDF.

        Returns:
            list: A list of tables extracted from the PDF.
        """
        tables = []
        with pdfplumber.open(self.file_path) as pdf:
            for page in pdf.pages:
                tables.extend(page.extract_tables())  # Append all tables from the pages
        return tables
    
    def extract_metadata(self):
        """Extract metadata from the PDF.

        Returns:
            dict: A dictionary containing metadata of the PDF.
        """
        metadata = {}
        with pdfplumber.open(self.file_path) as pdf:
            metadata = pdf.metadata  # Get metadata using pdfplumber
        return metadata


# Concrete DOCXLoader Class
class DOCXLoader(FileLoader):
    """Concrete implementation of FileLoader for DOCX files."""
    
    def __init__(self, file_path: str):
        """
        Initialize the DOCXLoader with the path to a DOCX file.

        Args:
            file_path (str): The path to the DOCX file.
        """
        self.file_path = file_path
        self.content = None

    def validate_file(self) -> bool:
        """Validate if the file is a DOCX and exists."""
        return self.file_path.endswith('.docx') and os.path.isfile(self.file_path)

    def load_file(self):
        """
        Load the DOCX file and return its content.

        Returns:
            Document: The Document object representing the loaded DOCX file.

        Raises:
            ValueError: If the DOCX file is invalid.
        """
        if self.validate_file():
            self.content = Document(self.file_path)  # Load the DOCX file
            return self.content
        raise ValueError("Invalid DOCX file")
    
    def extract_metadata(self):
        """Extract metadata from the DOCX file.

        Returns:
            dict: A dictionary containing metadata of the DOCX file.
        """
        metadata = {}
        doc = Document(self.file_path)
        core_properties = doc.core_properties  # Access core properties for metadata
        metadata = {
            'title': core_properties.title,
            'author': core_properties.author,
            'subject': core_properties.subject,
            'keywords': core_properties.keywords,
            'created': core_properties.created,
            'modified': core_properties.modified,
        }
        return metadata


# Concrete PPTLoader Class
class PPTLoader(FileLoader):
    """Concrete implementation of FileLoader for PPTX files."""
    
    def __init__(self, file_path: str):
        """
        Initialize the PPTLoader with the path to a PPTX file.

        Args:
            file_path (str): The path to the PPTX file.
        """
        self.file_path = file_path
        self.content = None

    def validate_file(self) -> bool:
        """Validate if the file is a PPTX and exists."""
        return self.file_path.endswith('.pptx') and os.path.isfile(self.file_path)

    def load_file(self):
        """
        Load the PPTX file and return its content.

        Returns:
            Presentation: The Presentation object representing the loaded PPTX file.

        Raises:
            ValueError: If the PPTX file is invalid.
        """
        if self.validate_file():
            self.content = Presentation(self.file_path)  # Load the PPTX file
            return self.content
        raise ValueError("Invalid PPT file")

    def extract_metadata(self):
        """Extract metadata from the PPTX file.

        Returns:
            dict: A dictionary containing metadata of the PPTX file.
        """
        metadata = {}
        presentation = Presentation(self.file_path)
        core_properties = presentation.core_properties  # Access core properties for metadata
        metadata = {
            'title': core_properties.title,
            'author': core_properties.author,
            'subject': core_properties.subject,
            'keywords': core_properties.keywords,
            'created': core_properties.created,
            'modified': core_properties.modified,
        }
        return metadata
