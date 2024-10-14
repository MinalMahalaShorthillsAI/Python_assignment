import os
import csv
import sqlite3
from io import BytesIO
from PIL import Image
from data_extractor import DataExtractor
from file_loader import PDFLoader, DOCXLoader, PPTLoader


class Storage:
    def __init__(self, extractor: DataExtractor, base_path: str):
        self.extractor = extractor
        self.base_path = base_path
        self.ensure_directories_exist()

    def ensure_directories_exist(self):
        os.makedirs(os.path.join(self.base_path, 'images'), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, 'tables'), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, 'text'), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, 'links'), exist_ok=True)

    def save_text(self):
        text = self.extractor.extract_text()
        file_type = self._get_file_type()
        text_file = os.path.join(self.base_path, 'text', f'{file_type}_text.txt')
        try:
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Successfully saved text to {text_file}")
        except Exception as e:
            print(f"Error saving text: {e}")

    def save_links(self):
        links = self.extractor.extract_links()
        file_type = self._get_file_type()
        links_file = os.path.join(self.base_path, 'links', f'{file_type}_links.txt')
        try:
            with open(links_file, 'w', encoding='utf-8') as f:
                for link in links:
                    f.write(f"{link}\n")
            print(f"Successfully saved links to {links_file}")
        except Exception as e:
            print(f"Error saving links: {e}")

    def save_images(self):
        images = self.extractor.extract_images()
        image_folder = os.path.join(self.base_path, 'images')
        
        # Determine the file type prefix
        file_type_prefix = self._get_file_type()  # This should return 'pdf', 'docx', or 'ppt'

        for idx, image_data in enumerate(images):
            try:
                if isinstance(image_data, dict):  # For pdfplumber images (metadata)
                    image_data = BytesIO(image_data['stream'].get_data())
                elif isinstance(image_data, bytes):  # For DOCX/PPT images (binary)
                    image_data = BytesIO(image_data)
                
                # Open the image using PIL
                image = Image.open(image_data)

                # Construct image path with appropriate prefix and extension
                image_path = os.path.join(image_folder, f'{file_type_prefix}_image_{idx + 1}.{image.format.lower()}')

                # Save the image
                image.save(image_path)
                print(f"Successfully saved image {idx + 1} to {image_path}")
            except Exception as e:
                print(f"Error saving image {idx + 1}: {e}")

    def save_tables(self):
        tables = self.extractor.extract_tables()
        file_type = self._get_file_type()
        table_folder = os.path.join(self.base_path, 'tables')
        for idx, table in enumerate(tables):
            csv_path = os.path.join(table_folder, f'table_{file_type}_{idx + 1}.csv')
            try:
                with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerows(table)
                print(f"Successfully saved table {idx + 1} to {csv_path}")
            except Exception as e:
                print(f"Error saving table {idx + 1}: {e}")


    def save_metadata(self):
        """Save metadata extracted from the file."""
        if isinstance(self.extractor.file_loader, PDFLoader):
            metadata = self.extractor.file_loader.extract_metadata()
        elif isinstance(self.extractor.file_loader, DOCXLoader):
            metadata = self.extractor.file_loader.extract_metadata()
        elif isinstance(self.extractor.file_loader, PPTLoader):
            metadata = self.extractor.file_loader.extract_metadata()
        else:
            print("Unknown file type. Unable to extract metadata.")
            return
        
        # Create a directory for metadata if it doesn't exist
        metadata_folder = os.path.join(self.base_path, 'metadata')
        os.makedirs(metadata_folder, exist_ok=True)
        
        # Save metadata to a file
        metadata_file = os.path.join(metadata_folder, f'{self._get_file_type()}_metadata.txt')
        
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                for key, value in metadata.items():
                    f.write(f"{key}: {value}\n")
            print(f"Successfully saved metadata to {metadata_file}")
        except Exception as e:
            print(f"Error saving metadata: {e}")


    def _get_file_type(self):
        """Helper method to get the file type (pdf, docx, ppt) based on the loader class."""
        if isinstance(self.extractor.file_loader, PDFLoader):
            return 'pdf'
        elif isinstance(self.extractor.file_loader, DOCXLoader):
            return 'docx'
        elif isinstance(self.extractor.file_loader, PPTLoader):
            return 'ppt'
        return 'unknown'

class StorageSQL:
    def __init__(self, extractor, db_path='extracted_data.db'):
        self.extractor = extractor
        self.conn = sqlite3.connect(db_path)  # Connect to SQLite database
        self.create_tables()

    def create_tables(self):
        """Create tables in the database if they don't exist."""
        cursor = self.conn.cursor()

        # Create tables for storing text, links, images, and tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_text (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_type TEXT,
                content TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_type TEXT,
                link TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_type TEXT,
                image BLOB
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_type TEXT,
                table_data TEXT
            )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_type TEXT,
            key TEXT,
            value TEXT
        )
    ''')
        self.conn.commit()

    def save_text(self):
        text = self.extractor.extract_text()
        file_type = self._get_file_type()

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO extracted_text (file_type, content)
            VALUES (?, ?)
        ''', (file_type, text))

        self.conn.commit()
        print("Text data saved to database.")

    def save_metadata(self):
        """Save metadata extracted from the file."""
        metadata = {}

        if isinstance(self.extractor.file_loader, PDFLoader):
            metadata = self.extractor.file_loader.extract_metadata()
        elif isinstance(self.extractor.file_loader, DOCXLoader):
            metadata = self.extractor.file_loader.extract_metadata()
        elif isinstance(self.extractor.file_loader, PPTLoader):
            metadata = self.extractor.file_loader.extract_metadata()
        else:
            print("Unknown file type. Unable to extract metadata.")
            return

        file_type = self._get_file_type()

        cursor = self.conn.cursor()
        for key, value in metadata.items():
            cursor.execute('''
                INSERT INTO extracted_metadata (file_type, key, value)
                VALUES (?, ?, ?)
            ''', (file_type, key, value))

        self.conn.commit()
        print("Metadata data saved to database.")

    def save_links(self):
        links = self.extractor.extract_links()
        file_type = self._get_file_type()

        cursor = self.conn.cursor()
        for link in links:
            if isinstance(link, tuple):
                # If link is a tuple (text, hyperlink), insert both text and hyperlink
                cursor.execute('''
                    INSERT INTO extracted_links (file_type, link)
                    VALUES (?, ?)
                ''', (file_type, link[1]))  # Store only the hyperlink part
            else:
                # If it's a simple hyperlink, store it as is
                cursor.execute('''
                    INSERT INTO extracted_links (file_type, link)
                    VALUES (?, ?)
                ''', (file_type, link))

        self.conn.commit()
        print("Link data saved to database.")


    def save_images(self):
        images = self.extractor.extract_images()
        file_type = self._get_file_type()

        cursor = self.conn.cursor()
        for idx, image_data in enumerate(images):
            try:
                if isinstance(image_data, dict):  # For pdfplumber images
                    image_data = BytesIO(image_data['stream'].get_data())
                elif isinstance(image_data, bytes):  # For DOCX/PPT images
                    image_data = BytesIO(image_data)

                # Convert image data to binary
                image = Image.open(image_data)
                img_byte_arr = BytesIO()
                image.save(img_byte_arr, format=image.format)
                img_byte_arr = img_byte_arr.getvalue()

                cursor.execute('''
                    INSERT INTO extracted_images (file_type, image)
                    VALUES (?, ?)
                ''', (file_type, img_byte_arr))

            except Exception as e:
                print(f"Error saving image {idx + 1}: {e}")

        self.conn.commit()
        print("Image data saved to database.")

    def save_tables(self):
        tables = self.extractor.extract_tables()
        file_type = self._get_file_type()

        cursor = self.conn.cursor()
        for idx, table in enumerate(tables):
            table_data = '\n'.join([','.join(row) for row in table])

            cursor.execute('''
                INSERT INTO extracted_tables (file_type, table_data)
                VALUES (?, ?)
            ''', (file_type, table_data))

        self.conn.commit()
        print("Table data saved to database.")

    def _get_file_type(self):
        """Helper method to get the file type (pdf, docx, ppt) based on the loader class."""
        if isinstance(self.extractor.file_loader, PDFLoader):
            return 'pdf'
        elif isinstance(self.extractor.file_loader, DOCXLoader):
            return 'docx'
        elif isinstance(self.extractor.file_loader, PPTLoader):
            return 'ppt'
        return 'unknown'

    def close(self):
        """Close the database connection."""
        self.conn.close()

    def display_data(self, table_name):
        cursor = self.conn.cursor()

        # Fetch all records from the specified table
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        if rows:
            print(f"\nData from {table_name}:")
            for row in rows:
                print(row)
        else:
            print(f"\nNo data found in {table_name}.")