import os
from abc import ABC, abstractmethod
from docx import Document
from pptx import Presentation


# Abstract FileLoader Class
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


# PDFLoader Class
class PDFLoader(FileLoader):
    """Concrete implementation of FileLoader for PDF files."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def validate_file(self) -> bool:
        return self.file_path.endswith('.pdf') and os.path.isfile(self.file_path)

    def load_file(self):
        if not self.validate_file():
            raise ValueError("Invalid PDF file")
        return self.file_path  # Return file path for extraction


# DOCXLoader Class
class DOCXLoader(FileLoader):
    """Concrete implementation of FileLoader for DOCX files."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def validate_file(self) -> bool:
        return self.file_path.endswith('.docx') and os.path.isfile(self.file_path)

    def load_file(self):
        if self.validate_file():
            return Document(self.file_path)  # Return the Document object for extraction
        raise ValueError("Invalid DOCX file")


# PPTLoader Class
class PPTLoader(FileLoader):
    """Concrete implementation of FileLoader for PPTX files."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def validate_file(self) -> bool:
        return self.file_path.endswith('.pptx') and os.path.isfile(self.file_path)

    def load_file(self):
        if self.validate_file():
            return Presentation(self.file_path)  # Return the Presentation object for extraction
        raise ValueError("Invalid PPTX file")
