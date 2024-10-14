from file_loader import PDFLoader, DOCXLoader, PPTLoader
from docx.opc.constants import RELATIONSHIP_TYPE as RT

class DataExtractor:
    def __init__(self, file_loader):
        self.file_loader = file_loader
        self.content = self.file_loader.load_file()

    def extract_text(self):
        if isinstance(self.file_loader, PDFLoader):
            return self.content
        elif isinstance(self.file_loader, DOCXLoader):
            return '\n'.join(paragraph.text for paragraph in self.content.paragraphs)
        elif isinstance(self.file_loader, PPTLoader):
            return '\n'.join(
                shape.text for slide in self.content.slides for shape in slide.shapes if hasattr(shape, "text")
            )
        return ""

    def extract_links(self):
        if isinstance(self.file_loader, PDFLoader):
            return self.file_loader.extract_links()
        links = []
        if isinstance(self.file_loader, DOCXLoader):
            for rel in self.content.part.rels.values():
                if rel.reltype == RT.HYPERLINK:
                    links.append(rel._target)
        elif isinstance(self.file_loader, PPTLoader):
            for slide in self.content.slides:
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            for run in paragraph.runs:
                                if run.hyperlink and run.hyperlink.address:
                                    links.append((run.text, run.hyperlink.address))
        return links

    def extract_images(self):
        """Extract images from the DOCX file."""
        images = []
        if isinstance(self.file_loader, PDFLoader):
            return self.file_loader.extract_images()

        if isinstance(self.file_loader, DOCXLoader):
            # Loop through all the relationships to find image references
            for rel in self.content.part.rels.values():
                if "image" in rel.target_ref:
                    # Retrieve the image binary data
                    image_data = rel.target_part.blob
                    images.append(image_data)
        elif isinstance(self.file_loader, PPTLoader):
            for slide in self.content.slides:
                for shape in slide.shapes:
                    if shape.shape_type == 13:  # Picture
                        images.append(shape.image.blob)
        return images

    def extract_tables(self):
        if isinstance(self.file_loader, PDFLoader):
            return self.file_loader.extract_tables()
        tables = []
        if isinstance(self.file_loader, DOCXLoader):
            for table in self.content.tables:
                table_data = [[cell.text for cell in row.cells] for row in table.rows]
                tables.append(table_data)
        elif isinstance(self.file_loader, PPTLoader):
            for slide in self.content.slides:
                for shape in slide.shapes:
                    if shape.has_table:
                        table_data = [[cell.text for cell in row.cells] for row in shape.table.rows]
                        tables.append(table_data)
        return tables
