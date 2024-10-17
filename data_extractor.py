from docx.opc.constants import RELATIONSHIP_TYPE as RT
from file_loader import PDFLoader, PPTLoader, DOCXLoader
from pdfminer.high_level import extract_text
import pdfplumber

class DataExtractor:
    """A class to extract text, links, images, and tables from various document formats."""

    def __init__(self, file_loader):
        """
        Initialize the DataExtractor with a specific file loader.

        Args:
            file_loader: An instance of PDFLoader, DOCXLoader, or PPTLoader that handles loading files.
        """
        self.file_loader = file_loader
        self.content = self.file_loader.load_file()  # Load the file using the provided file loader

    def extract_text(self):
        """
        Extract text content from the loaded file.

        Returns:
            str: The extracted text as a single string.
        """
        if isinstance(self.file_loader, PDFLoader):
            text = extract_text(self.file_loader.file_path)
            if text.strip():
                return text # Directly return PDF content
        elif isinstance(self.file_loader, DOCXLoader):
            # Join all paragraph texts in a DOCX document
            return '\n'.join(paragraph.text for paragraph in self.content.paragraphs)
        elif isinstance(self.file_loader, PPTLoader):
            # Join all shape texts from each slide in a PPT presentation
            return '\n'.join(
                shape.text for slide in self.content.slides for shape in slide.shapes if hasattr(shape, "text")
            )
        return ""

    def extract_links(self):
        """Extract hyperlinks from the loaded file."""
        if isinstance(self.file_loader, PDFLoader):
            return self.extract_pdf_links(self.file_loader.file_path)
        elif isinstance(self.file_loader, DOCXLoader):
            return self.extract_docx_links()
        elif isinstance(self.file_loader, PPTLoader):
            return self.extract_ppt_links()
        return []

    def extract_pdf_links(self, file_path):
        """Extract links from a PDF file."""
        links = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                if page.annots:
                    for annotation in page.annots:
                        if annotation.get("uri"):
                            links.append(annotation["uri"])
        return links

    def extract_docx_links(self):
        """Extract links from a DOCX file."""
        links = []
        for rel in self.content.part.rels.values():
            if rel.reltype == RT.HYPERLINK:
                links.append(rel._target)
        return links

    def extract_ppt_links(self):
        """Extract links from a PPTX file."""
        links = []
        for slide in self.content.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            if run.hyperlink and run.hyperlink.address:
                                links.append((run.hyperlink.address))
        return links

    def extract_images(self):
        """Extract images from the loaded file."""
        if isinstance(self.file_loader, PDFLoader):
            return self.extract_pdf_images(self.file_loader.file_path)
        elif isinstance(self.file_loader, DOCXLoader):
            return self.extract_docx_images()
        elif isinstance(self.file_loader, PPTLoader):
            return self.extract_ppt_images()
        return []

    def extract_pdf_images(self, file_path):
        """Extract images from a PDF file."""
        images = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                if page.images:
                    images.extend(page.images)
        return images

    def extract_docx_images(self):
        """Extract images from a DOCX file."""
        images = []
        for rel in self.content.part.rels.values():
            if "image" in rel.target_ref:
                images.append(rel.target_part.blob)
        return images

    def extract_ppt_images(self):
        """Extract images from a PPTX file."""
        images = []
        for slide in self.content.slides:
            for shape in slide.shapes:
                if shape.shape_type == 13:  # Shape type 13 corresponds to Picture
                    images.append(shape.image.blob)
        return images

    def extract_tables(self):
        """Extract tables from the loaded file."""
        if isinstance(self.file_loader, PDFLoader):
            return self.extract_pdf_tables(self.file_loader.file_path)
        elif isinstance(self.file_loader, DOCXLoader):
            return self.extract_docx_tables()
        elif isinstance(self.file_loader, PPTLoader):
            return self.extract_ppt_tables()
        return []

    def extract_pdf_tables(self, file_path):
        """Extract tables from a PDF file."""
        tables = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                tables.extend(page.extract_tables())
        return tables

    def extract_docx_tables(self):
        """Extract tables from a DOCX file."""
        tables = []
        for table in self.content.tables:
            table_data = [[cell.text for cell in row.cells] for row in table.rows]
            tables.append(table_data)
        return tables

    def extract_ppt_tables(self):
        """Extract tables from a PPTX file."""
        tables = []
        for slide in self.content.slides:
            for shape in slide.shapes:
                if shape.has_table:
                    table_data = [[cell.text for cell in row.cells] for row in shape.table.rows]
                    tables.append(table_data)
        return tables

    def extract_metadata(self):
        """Extract metadata from the loaded file."""
        if isinstance(self.file_loader, PDFLoader):
            return self.extract_pdf_metadata(self.file_loader.file_path)
        elif isinstance(self.file_loader, DOCXLoader):
            return self.extract_docx_metadata()
        elif isinstance(self.file_loader, PPTLoader):
            return self.extract_ppt_metadata()
        return {}

    def extract_pdf_metadata(self, file_path):
        """Extract metadata from a PDF file."""
        with pdfplumber.open(file_path) as pdf:
            return pdf.metadata

        core_properties = self.content.core_properties
        return {
            'title': core_properties.title,
            'author': core_properties.author,
            'subject': core_properties.subject,
            'keywords': core_properties.keywords,
            'created': core_properties.created,
            'modified': core_properties.modified,
        }

    def extract_ppt_metadata(self):
        """Extract metadata from a PPTX file."""
        core_properties = self.content.core_properties
        return {
            'title': core_properties.title,
            'author': core_properties.author,
            'subject': core_properties.subject,
            'keywords': core_properties.keywords,
            'created': core_properties.created,
            'modified': core_properties.modified,
        }
    
    def extract_docx_metadata(self):
        """Extract metadata from a PPTX file."""
        core_properties = self.content.core_properties
        return {
            'title': core_properties.title,
            'author': core_properties.author,
            'subject': core_properties.subject,
            'keywords': core_properties.keywords,
            'created': core_properties.created,
            'modified': core_properties.modified,
        }
