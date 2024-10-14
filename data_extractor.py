from file_loader import PDFLoader, DOCXLoader, PPTLoader
from docx.opc.constants import RELATIONSHIP_TYPE as RT

class DataExtractor:
    """A class to extract text, links, images, and tables from various document formats."""

    def __init__(self, file_loader):
        """
        Initialize the DataExtractor with a specific file loader.

        Args:
            file_loader: An instance of PDFLoader, DOCXLoader, or PPTLoader that handles loading files.
        """
        self.file_loader = file_loader
        # Load the content of the file using the provided file loader
        self.content = self.file_loader.load_file()

    def extract_text(self):
        """
        Extract text content from the loaded file.

        Returns:
            str: The extracted text as a single string.
        """
        if isinstance(self.file_loader, PDFLoader):
            return self.content  # Directly return PDF content
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
        """
        Extract hyperlinks from the loaded file.

        Returns:
            list: A list of hyperlinks or tuples of (link text, link address).
        """
        if isinstance(self.file_loader, PDFLoader):
            return self.file_loader.extract_links()  # Extract links from a PDF
        links = []
        if isinstance(self.file_loader, DOCXLoader):
            # Extract hyperlinks from a DOCX document
            for rel in self.content.part.rels.values():
                if rel.reltype == RT.HYPERLINK:
                    links.append(rel._target)  # Add the target of the hyperlink
        elif isinstance(self.file_loader, PPTLoader):
            # Extract hyperlinks from each slide in a PPT presentation
            for slide in self.content.slides:
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            for run in paragraph.runs:
                                if run.hyperlink and run.hyperlink.address:
                                    links.append((run.text, run.hyperlink.address))  # Add text and address as a tuple
        return links

    def extract_images(self):
        """
        Extract images from the loaded file.

        Returns:
            list: A list of image binary data.
        """
        images = []
        if isinstance(self.file_loader, PDFLoader):
            return self.file_loader.extract_images()  # Extract images from a PDF

        if isinstance(self.file_loader, DOCXLoader):
            # Loop through all the relationships to find image references in a DOCX document
            for rel in self.content.part.rels.values():
                if "image" in rel.target_ref:
                    # Retrieve the image binary data
                    image_data = rel.target_part.blob
                    images.append(image_data)  # Append the image data to the list
        elif isinstance(self.file_loader, PPTLoader):
            # Extract images from each slide in a PPT presentation
            for slide in self.content.slides:
                for shape in slide.shapes:
                    if shape.shape_type == 13:  # Shape type 13 corresponds to Picture
                        images.append(shape.image.blob)  # Append the image data to the list
        return images

    def extract_tables(self):
        """
        Extract tables from the loaded file.

        Returns:
            list: A list of tables, where each table is represented as a list of lists (rows and columns).
        """
        if isinstance(self.file_loader, PDFLoader):
            return self.file_loader.extract_tables()  # Extract tables from a PDF
        tables = []
        if isinstance(self.file_loader, DOCXLoader):
            # Extract tables from a DOCX document
            for table in self.content.tables:
                # Create a list of lists for each table
                table_data = [[cell.text for cell in row.cells] for row in table.rows]
                tables.append(table_data)  # Append the table data to the list
        elif isinstance(self.file_loader, PPTLoader):
            # Extract tables from each slide in a PPT presentation
            for slide in self.content.slides:
                for shape in slide.shapes:
                    if shape.has_table:
                        # Create a list of lists for each table shape
                        table_data = [[cell.text for cell in row.cells] for row in shape.table.rows]
                        tables.append(table_data)  # Append the table data to the list
        return tables
