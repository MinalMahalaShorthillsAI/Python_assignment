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
        text = self.extractor.extract_text().strip()
        file_type = self._get_file_type()
        text_file = os.path.join(self.base_path, 'text', f'{file_type}_text.txt')
        try:
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Successfully saved text to {text_file}")
        except Exception as e:
            print(f"Error saving text: {e}")

    def save_links(self):
        self._save_to_file('links', 'links', lambda: self.extractor.extract_links(), format_func=str)

    def save_images(self):
        images = self.extractor.extract_images()
        image_folder = os.path.join(self.base_path, 'images')
        file_type_prefix = self._get_file_type()

        for idx, image_data in enumerate(images):
            try:
                image_data = self._prepare_image_data(image_data)
                image = Image.open(image_data)
                image_path = os.path.join(image_folder, f'{file_type_prefix}_image_{idx + 1}.{image.format.lower()}')
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
            self._write_csv(csv_path, table)

    def save_metadata(self):
        metadata = self.extractor.extract_metadata()
        metadata_folder = os.path.join(self.base_path, 'metadata')
        os.makedirs(metadata_folder, exist_ok=True)
        metadata_file = os.path.join(metadata_folder, f'{self._get_file_type()}_metadata.txt')

        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                for key, value in metadata.items():
                    f.write(f"{key}: {value}\n")
            print(f"Successfully saved metadata to {metadata_file}")
        except Exception as e:
            print(f"Error saving metadata: {e}")

    def _save_to_file(self, folder_name, file_type, extract_func, format_func=lambda x: x):
        """General method to save data to files."""
        data = extract_func()
        file_path = os.path.join(self.base_path, folder_name, f'{self._get_file_type()}_{folder_name}.txt')

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(f"{format_func(item)}\n")
            print(f"Successfully saved {folder_name} to {file_path}")
        except Exception as e:
            print(f"Error saving {folder_name}: {e}")

    def _write_csv(self, file_path, data):
        """Helper method to write data to a CSV file."""
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(data)
            print(f"Successfully saved table to {file_path}")
        except Exception as e:
            print(f"Error saving table: {e}")

    def _prepare_image_data(self, image_data):
        """Prepare image data for saving."""
        if isinstance(image_data, dict):  # For pdfplumber images
            return BytesIO(image_data['stream'].get_data())
        elif isinstance(image_data, bytes):  # For DOCX/PPT images
            return BytesIO(image_data)
        return image_data  # Handle any unexpected cases

    def _get_file_type(self):
        """Helper method to get the file type (pdf, docx, ppt) based on the loader class."""
        file_loader_mapping = {
            PDFLoader: 'pdf',
            DOCXLoader: 'docx',
            PPTLoader: 'ppt'
        }

        for loader_class, file_type in file_loader_mapping.items():
            if isinstance(self.extractor.file_loader, loader_class):
                return file_type
        
        return 'unknown'


class StorageSQL:
    def __init__(self, extractor: DataExtractor, db_path='extracted_data.db'):
        self.extractor = extractor
        self.conn = sqlite3.connect(db_path)  # Connect to SQLite database
        self.create_tables()

    def create_tables(self):
        """Create tables in the database if they don't exist."""
        cursor = self.conn.cursor()
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
        self._save_to_db('extracted_text', 'content', self.extractor.extract_text)

    def save_links(self):
        self._save_to_db('extracted_links', 'link', lambda: self.extractor.extract_links(), is_link=True)

    def save_images(self):
        images = self.extractor.extract_images()
        file_type = self._get_file_type()

        cursor = self.conn.cursor()
        for idx, image_data in enumerate(images):
            try:
                image_data = self._prepare_image_data(image_data)
                img_byte_arr = self._get_image_bytes(image_data)

                cursor.execute('''
                    INSERT INTO extracted_images (file_type, image)
                    VALUES (?, ?)
                ''', (file_type, img_byte_arr))

            except Exception as e:
                print(f"Error saving image {idx + 1}: {e}")

        self.conn.commit()
        print("Image data saved to database.")


    def save_metadata(self):
        metadata = self.extractor.extract_metadata()
        file_type = self._get_file_type()
        cursor = self.conn.cursor()

        for key, value in metadata.items():
            cursor.execute('''
                INSERT INTO extracted_metadata (file_type, key, value)
                VALUES (?, ?, ?)
            ''', (file_type, key, value))

        self.conn.commit()
        print("Metadata data saved to database.")

    def _save_to_db(self, table_name, column_name, extract_func, is_link=False):
        """General method to save data to the database."""
        data = extract_func()
        file_type = self._get_file_type()

        cursor = self.conn.cursor()
        for item in data:
            if is_link and isinstance(item, tuple):
                item = item[1]  # Only save the hyperlink part
            cursor.execute(f'''
                INSERT INTO {table_name} (file_type, {column_name})
                VALUES (?, ?)
            ''', (file_type, item))

        self.conn.commit()
        print(f"{column_name.capitalize()} data saved to database.")

    def save_tables(self):
        tables = self.extractor.extract_tables()
        file_type = self._get_file_type()

        cursor = self.conn.cursor()
        for idx, table in enumerate(tables):
            # Convert None to empty string in the table data
            table_data = '\n'.join([','.join(str(item) if item is not None else '' for item in row) for row in table])

            cursor.execute('''
                INSERT INTO extracted_tables (file_type, table_data)
                VALUES (?, ?)
            ''', (file_type, table_data))

        self.conn.commit()
        print("Table data saved to database.")

    def _get_image_bytes(self, image_data):
        """Convert image data to binary format for storage."""
        img_byte_arr = BytesIO()
        image = Image.open(image_data)
        image.save(img_byte_arr, format=image.format)
        return img_byte_arr.getvalue()

    def _prepare_image_data(self, image_data):
        """Prepare image data for saving."""
        if isinstance(image_data, dict):  # For pdfplumber images
            return BytesIO(image_data['stream'].get_data())
        elif isinstance(image_data, bytes):  # For DOCX/PPT images
            return BytesIO(image_data)
        return image_data  # Handle any unexpected cases

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
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        if rows:
            print(f"\nData from {table_name}:")
            for row in rows:
                print(row)
        else:
            print(f"\nNo data found in {table_name}.")
