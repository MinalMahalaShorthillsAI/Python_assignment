import os
from abc import ABC, abstractmethod
from docx import Document
from pptx import Presentation

# Abstract FileLoader Class
class FileLoader(ABC):
    """Abstract base class for loading different file types.
    
    This class defines the interface for file loaders that handle different types of files.
    Any class inheriting from FileLoader must implement the validate_file and load_file methods.
    """

    @abstractmethod
    def validate_file(self) -> bool:
        """Check if the file is valid.
        
        This method must be implemented by subclasses to validate if the provided file
        is of the correct type and exists at the specified path.
        """
        pass

    @abstractmethod
    def load_file(self):
        """Load the file and return its content.
        
        This method must be implemented by subclasses to load the file and return its content,
        whether as a raw file path, an object, or some other format suitable for processing.
        """
        pass


# PDFLoader Class
class PDFLoader(FileLoader):
    """Concrete implementation of FileLoader for PDF files.
    
    This class provides methods to validate and load PDF files.
    """

    def __init__(self, file_path: str):
        """Initialize PDFLoader with the path to the PDF file."""
        self.file_path = file_path

    def validate_file(self) -> bool:
        """Check if the file is a valid PDF file and exists.
        
        Returns True if the file is a .pdf file and exists at the provided path, False otherwise.
        """
        return self.file_path.endswith('.pdf') and os.path.isfile(self.file_path)

    def load_file(self):
        """Load the PDF file if valid and return the file path for further extraction.
        
        Raises a ValueError if the file is invalid.
        """
        if not self.validate_file():
            raise ValueError("Invalid PDF file")
        return self.file_path  # Return file path for extraction


# DOCXLoader Class
class DOCXLoader(FileLoader):
    """Concrete implementation of FileLoader for DOCX files.
    
    This class provides methods to validate and load DOCX files.
    """

    def __init__(self, file_path: str):
        """Initialize DOCXLoader with the path to the DOCX file."""
        self.file_path = file_path

    def validate_file(self) -> bool:
        """Check if the file is a valid DOCX file and exists.
        
        Returns True if the file is a .docx file and exists at the provided path, False otherwise.
        """
        return self.file_path.endswith('.docx') and os.path.isfile(self.file_path)

    def load_file(self):
        """Load the DOCX file if valid and return the Document object for extraction.
        
        Raises a ValueError if the file is invalid.
        """
        if self.validate_file():
            return Document(self.file_path)  # Return the Document object for extraction
        raise ValueError("Invalid DOCX file")


# PPTLoader Class
class PPTLoader(FileLoader):
    """Concrete implementation of FileLoader for PPTX files.
    
    This class provides methods to validate and load PPTX files.
    """

    def __init__(self, file_path: str):
        """Initialize PPTLoader with the path to the PPTX file."""
        self.file_path = file_path

    def validate_file(self) -> bool:
        """Check if the file is a valid PPTX file and exists.
        
        Returns True if the file is a .pptx file and exists at the provided path, False otherwise.
        """
        return self.file_path.endswith('.pptx') and os.path.isfile(self.file_path)

    def load_file(self):
        """Load the PPTX file if valid and return the Presentation object for extraction.
        
        Raises a ValueError if the file is invalid.
        """
        if self.validate_file():
            return Presentation(self.file_path)  # Return the Presentation object for extraction
        raise ValueError("Invalid PPTX file")
