import os
import csv
import mysql.connector
from abc import ABC, abstractmethod
from PIL import Image
from io import BytesIO
from file_loader import PDFLoader, DOCXLoader, PPTLoader


# Base abstract class for data storage
class DataStorage(ABC):
    def __init__(self, extractor):
        self.extractor = extractor

    @abstractmethod
    def save_text(self):
        """Save extracted text data."""
        pass

    @abstractmethod
    def save_links(self):
        """Save extracted links."""
        pass

    @abstractmethod
    def save_images(self):
        """Save extracted images."""
        pass

    @abstractmethod
    def save_tables(self):
        """Save extracted tables."""
        pass

    @abstractmethod
    def save_metadata(self):
        """Save extracted metadata."""
        pass

# Concrete implementation for file-based storage
class Storage(DataStorage):
    def __init__(self, extractor, base_path):
        super().__init__(extractor)
        self.base_path = base_path
        self._folders = ['images', 'tables', 'text', 'links', 'metadata']
        self.ensure_directories_exist()

    def ensure_directories_exist(self):
        """Create necessary directories if they don't exist."""
        for folder in self._folders:
            os.makedirs(os.path.join(self.base_path, folder), exist_ok=True)

    def save_text(self):
        """Extract and save text to a file."""
        text = self.extractor.extract_text().strip()
        file_type = self._get_file_type()
        text_file = os.path.join(self.base_path, 'text', f'{file_type}_text.txt')
        
        self._attempt_save(text_file, text, "Text")

    def save_links(self):
        """Save extracted links to a file."""
        links = self.extractor.extract_links()
        file_path = os.path.join(self.base_path, 'links', f'links_{self._get_file_type()}.txt')
        
        self._attempt_save(file_path, '\n'.join(links), "Links")

    def save_images(self):
        """Save extracted images to individual files."""
        images = self.extractor.extract_images()
        for idx, image_data in enumerate(images):
            try:
                image = Image.open(self._prepare_image_data(image_data))
                image_path = os.path.join(self.base_path, 'images', f'{self._get_file_type()}_image_{idx + 1}.{image.format.lower()}')
                image.save(image_path)
                print(f"Image {idx + 1} successfully saved.")
            except Exception as e:
                print(f"Error saving image {idx + 1}: {e}")

    def save_tables(self):
        """Save extracted tables in CSV format."""
        tables = self.extractor.extract_tables()
        for idx, table in enumerate(tables):
            file_path = os.path.join(self.base_path, 'tables', f'table_{self._get_file_type()}_{idx + 1}.csv')
            table_data = '\n'.join([','.join(map(str, row)) for row in table])
            
            self._attempt_save(file_path, table_data, f"Table {idx + 1}")

    def save_metadata(self):
        """Save extracted metadata to a file."""
        metadata = self.extractor.extract_metadata()
        file_path = os.path.join(self.base_path, 'metadata', f'metadata_{self._get_file_type()}.txt')
        
        metadata_content = '\n'.join(f"{key}: {value}" for key, value in metadata.items())
        self._attempt_save(file_path, metadata_content, "Metadata")

    def _attempt_save(self, file_path, data, data_type):
        """Generalized method to attempt saving data with error handling."""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(data)
            print(f"{data_type} successfully saved to {file_path}")
        except Exception as e:
            print(f"Error saving {data_type}: {e}")

    def _save_to_file(self, file_path, data):
        """Helper method to save data to a file."""
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(data)

    def _write_csv(self, file_path, data):
        """Helper method to write table data to a CSV file."""
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            csv.writer(file).writerows(data)
            print(f"Successfully saved table to {file_path}")

    def _prepare_image_data(self, image_data):
        """Prepare image data for saving."""
        if isinstance(image_data, dict):
            return BytesIO(image_data['stream'].get_data())
        if isinstance(image_data, bytes):
            return BytesIO(image_data)
        return image_data

    def _get_file_type(self):
        """Determine the file type based on the file loader used."""
        file_loader_mapping = {PDFLoader: 'pdf', DOCXLoader: 'docx', PPTLoader: 'ppt'}
        return next((file_type for loader_class, file_type in file_loader_mapping.items()
                     if isinstance(self.extractor.file_loader, loader_class)), 'unknown')

# Concrete implementation for SQL-based storage
class StorageSQL(DataStorage):
    def __init__(self, extractor, db_config):
        super().__init__(extractor)
        self.conn = mysql.connector.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """Create tables in the MySQL database for storing data."""
        cursor = self.conn.cursor()
        tables_sql = [
            '''
            CREATE TABLE IF NOT EXISTS extracted_text (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_type VARCHAR(255),
                content TEXT
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS extracted_links (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_type VARCHAR(255),
                link TEXT
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS extracted_images (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_type VARCHAR(255),
                image LONGBLOB
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS extracted_tables (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_type VARCHAR(255),
                table_data TEXT
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS extracted_metadata (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_type VARCHAR(255),
                `key` VARCHAR(255),
                `value` TEXT
            )
            '''
        ]
        for sql in tables_sql:
            cursor.execute(sql)
        self.conn.commit()

    def save_text(self):
        """Save extracted text to the database."""
        text = self.extractor.extract_text()
        file_type = self._get_file_type()
        
        self._attempt_sql_insert('extracted_text', [file_type, text], "Text")

    def save_links(self):
        """Save extracted links to the database."""
        links = self.extractor.extract_links()
        file_type = self._get_file_type()
        
        for link in links:
            self._attempt_sql_insert('extracted_links', [file_type, link], "Link")

    def save_images(self):
        """Save extracted images to the database."""
        images = self.extractor.extract_images()
        file_type = self._get_file_type()
        
        for image_data in images:
            try:
                img_byte_arr = self._get_image_bytes(image_data)
                self._attempt_sql_insert('extracted_images', [file_type, img_byte_arr], "Image")
            except Exception as e:
                print(f"Error saving image: {e}")

    def save_tables(self):
        """Save extracted tables to the database."""
        tables = self.extractor.extract_tables()
        file_type = self._get_file_type()
        
        for idx, table in enumerate(tables):
            table_data = '\n'.join([','.join(map(str, row)) for row in table])
            self._attempt_sql_insert('extracted_tables', [file_type, table_data], f"Table {idx + 1}")

    def save_metadata(self):
        """Save extracted metadata to the database."""
        metadata = self.extractor.extract_metadata()
        file_type = self._get_file_type()
        
        for key, value in metadata.items():
            self._attempt_sql_insert('extracted_metadata', [file_type, key, value], f"Metadata ({key})")

    def _attempt_sql_insert(self, table_name, values, data_type):
        """Generalized method to attempt inserting data into SQL with error handling."""
        cursor = self.conn.cursor()
        placeholders = ', '.join(['%s'] * len(values))
        sql = f'INSERT INTO {table_name} VALUES (NULL, {placeholders})'  # Updated to auto-increment ID
        
        try:
            cursor.execute(sql, values)
            self.conn.commit()
            print(f"{data_type} successfully saved to SQL database.")
        except Exception as e:
            print(f"Error saving {data_type} to SQL database: {e}")

    def _insert_into_db(self, table_name, values):
        """Insert data into the specified table in the database."""
        cursor = self.conn.cursor()
        placeholders = ', '.join(['%s'] * len(values))
        sql = f'INSERT INTO {table_name} VALUES (NULL, {placeholders})'  # Updated to auto-increment ID
        try:
            cursor.execute(sql, values)
            self.conn.commit()
        except Exception as e:
            print(f"Error inserting into {table_name}: {e}")

    def _get_image_bytes(self, image_data):
        """Convert image data to bytes."""
        img_byte_arr = BytesIO()
        image = Image.open(self._prepare_image_data(image_data))
        image.save(img_byte_arr, format=image.format)
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()

    def _prepare_image_data(self, image_data):
        """Prepare image data for saving."""
        if isinstance(image_data, dict):
            return BytesIO(image_data['stream'].get_data())
        if isinstance(image_data, bytes):
            return BytesIO(image_data)
        return image_data

    def _get_file_type(self):
        """Determine the file type based on the file loader used."""
        file_loader_mapping = {PDFLoader: 'pdf', DOCXLoader: 'docx', PPTLoader: 'ppt'}
        return next((file_type for loader_class, file_type in file_loader_mapping.items()
                     if isinstance(self.extractor.file_loader, loader_class)), 'unknown')

    def close(self):
        """Close the database connection."""
        self.conn.close()
        print("Database connection closed.")