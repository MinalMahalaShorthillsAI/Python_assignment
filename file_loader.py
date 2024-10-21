import os
from abc import ABC, abstractmethod
from docx import Document
from pptx import Presentation

# Abstract FileLoader Class
class FileLoader(ABC):
    """Abstract base class for loading different file types."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def validate_and_load_file(self):
        """Validate the file and load its content if valid.
        
        This method checks if the file exists and if the file extension is correct.
        If valid, it calls the specific method to load the content.
        """
        if not os.path.isfile(self.file_path):
            raise ValueError(f"File does not exist: {self.file_path}")
        if not self.file_path.endswith(self.file_extension):
            raise ValueError(f"Invalid file type: Expected {self.file_extension}")

        return self.load_file()  # Load the file content

    @abstractmethod
    def load_file(self):
        """Abstract method to load the file's content.
        
        Subclasses must implement this to return the specific content.
        """
        pass


class PDFLoader(FileLoader):
    file_extension = '.pdf'

    def load_file(self):
        """Load and return the file path for PDF extraction."""
        return self.file_path


class DOCXLoader(FileLoader):
    file_extension = '.docx'

    def load_file(self):
        """Load and return the Document object for DOCX extraction."""
        return Document(self.file_path)


class PPTLoader(FileLoader):
    file_extension = '.pptx'

    def load_file(self):
        """Load and return the Presentation object for PPTX extraction."""
        return Presentation(self.file_path)
