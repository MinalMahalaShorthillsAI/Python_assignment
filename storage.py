import os
import csv
from io import BytesIO
import mysql.connector
from PIL import Image
from data_extractor import DataExtractor
from file_loader import PDFLoader, DOCXLoader, PPTLoader

class Storage:
    def __init__(self, extractor: DataExtractor, base_path: str):
        self.extractor = extractor
        self.base_path = base_path
        self._folders = ['images', 'tables', 'text', 'links', 'metadata']
        self.ensure_directories_exist()

    def ensure_directories_exist(self):
        """Create necessary directories if they don't exist."""
        for folder in self._folders:
            os.makedirs(os.path.join(self.base_path, folder), exist_ok=True)

    def save_text(self):
        """Extract and save text to a file."""
        text = self.extractor.extract_text().strip()  # Get extracted text
        file_type = self._get_file_type()  # Get file type (e.g., pdf, docx)
        text_file = os.path.join(self.base_path, 'text', f'{file_type}_text.txt')  # File path to save text

        try:
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text)  # Write text to file
            print(f"Successfully saved text to {text_file}")
        except Exception as e:
            print(f"Error saving text: {e}")  # Handle errors in saving text

    def save_links(self):
        """Extract and save links to a file."""
        self._save_to_file('links', 'links', self.extractor.extract_links, format_func=str)

    def save_images(self):
        """Extract and save images to individual files."""
        images = self.extractor.extract_images()
        for idx, image_data in enumerate(images):
            self._save_image(image_data, idx)

    def save_tables(self):
        """Extract and save tables in CSV format."""
        for idx, table in enumerate(self.extractor.extract_tables()):
            self._write_csv(os.path.join(self.base_path, 'tables', f'table_{self._get_file_type()}_{idx + 1}.csv'), table)

    def save_metadata(self):
        """Extract and save metadata to a file."""
        self._save_to_file('metadata', 'metadata', self.extractor.extract_metadata, format_func=lambda x: f"{x[0]}: {x[1]}")

    def _save_to_file(self, folder_name, file_type, extract_func, format_func=lambda x: x):
        """General method to save extracted data to a file."""
        data = extract_func()
        file_path = os.path.join(self.base_path, folder_name, f'{self._get_file_type()}_{folder_name}.txt')
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if isinstance(data, dict):
                    data = data.items()  # Handle metadata dict case
                for item in data:
                    f.write(f"{format_func(item)}\n")
            print(f"Successfully saved {folder_name} to {file_path}")
        except Exception as e:
            print(f"Error saving {folder_name}: {e}")

    def _save_image(self, image_data, idx):
        """Helper method to save individual images."""
        try:
            image_data = self._prepare_image_data(image_data)
            image = Image.open(image_data)
            image_path = os.path.join(self.base_path, 'images', f'{self._get_file_type()}_image_{idx + 1}.{image.format.lower()}')
            image.save(image_path)
            print(f"Successfully saved image {idx + 1} to {image_path}")
        except Exception as e:
            print(f"Error saving image {idx + 1}: {e}")

    def _write_csv(self, file_path, data):
        """Helper method to write table data to a CSV file."""
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                csv.writer(file).writerows(data)
            print(f"Successfully saved table to {file_path}")
        except Exception as e:
            print(f"Error saving table: {e}")

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

# StorageSQL class for saving extracted content to a MySQL database
class StorageSQL:
    def __init__(self, extractor: DataExtractor, db_config):
        self.extractor = extractor  # DataExtractor instance to extract content
        self.conn = mysql.connector.connect(**db_config)  # Establish database connection using provided config
        self.create_tables()  # Ensure necessary tables are created

    def create_tables(self):
        """Create tables in the MySQL database for storing text, links, images, tables, and metadata."""
        cursor = self.conn.cursor()  # Create a cursor for executing SQL queries
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
            cursor.execute(sql)  # Execute each SQL statement
        self.conn.commit()  # Commit the changes to the database

    def save_text(self):
        """Extract and save text to the database."""
        self._save_to_db('extracted_text', 'content', self.extractor.extract_text)

    def save_links(self):
        """Extract and save links to the database."""
        self._save_to_db('extracted_links', 'link', self.extractor.extract_links, is_link=True)

    def save_images(self):
        """Extract and save images to the database."""
        images = self.extractor.extract_images()  # Get extracted images
        file_type = self._get_file_type()  # Get file type (e.g., pdf, docx)

        for idx, image_data in enumerate(images):
            try:
                image_data = self._prepare_image_data(image_data)  # Prepare image data for saving
                img_byte_arr = self._get_image_bytes(image_data)  # Convert image to binary
                self._insert_into_db('extracted_images', ['file_type', 'image'], [file_type, img_byte_arr])
            except Exception as e:
                print(f"Error saving image {idx + 1}: {e}")  # Handle image save errors
        print("Image data saved to database.")

    def save_metadata(self):
        """Extract and save metadata to the database."""
        metadata = self.extractor.extract_metadata()  # Get extracted metadata
        file_type = self._get_file_type()  # Get file type (e.g., pdf, docx)
        
        for key, value in metadata.items():
            self._insert_into_db('extracted_metadata', ['file_type', 'key', 'value'], [file_type, key, value])
        print("Metadata saved to database.")

    def save_tables(self):
        """Extract and save tables to the database."""
        tables = self.extractor.extract_tables()  # Get extracted tables
        file_type = self._get_file_type()  # Get file type (e.g., pdf, docx)

        for idx, table in enumerate(tables):
            # Convert table rows to CSV format
            table_data = '\n'.join([','.join(str(item) if item is not None else '' for item in row) for row in table])
            self._insert_into_db('extracted_tables', ['file_type', 'table_data'], [file_type, table_data])
        print("Table data saved to database.")

    def _save_to_db(self, table_name, column_name, extract_func, is_link=False):
        """General method to save extracted data (e.g., text, links) to the database."""
        data = extract_func()  # Extract data using the provided function
        file_type = self._get_file_type()  # Get file type (e.g., pdf, docx)

        for item in data:
            if is_link and isinstance(item, tuple):
                item = item[1]  # Extract only the hyperlink if data contains tuple
            self._insert_into_db(table_name, ['file_type', column_name], [file_type, item])
        print(f"{column_name.capitalize()} data saved to database.")

    def _insert_into_db(self, table_name, columns, values):
        """Helper method to insert data into the database."""
        cursor = self.conn.cursor()  # Create a cursor for executing SQL queries
        columns_str = ', '.join([f'`{col}`' for col in columns])  # Join column names with backticks for SQL safety
        placeholders = ', '.join(['%s'] * len(values))  # Create placeholders for values
        sql = f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})'  # Build SQL query
        cursor.execute(sql, values)  # Execute SQL query with provided values
        self.conn.commit()  # Commit changes

    def _get_image_bytes(self, image_data):
        """Convert image data to binary format for storage in the database."""
        img_byte_arr = BytesIO()  # Create a BytesIO object
        image = Image.open(image_data)  # Open the image
        image.save(img_byte_arr, format=image.format)  # Save image in binary format
        return img_byte_arr.getvalue()  # Return binary data

    def _prepare_image_data(self, image_data):
        """Prepare image data for saving by converting to a BytesIO stream if necessary."""
        if isinstance(image_data, dict):  # If the image data is a dict (e.g., from pdfplumber)
            return BytesIO(image_data['stream'].get_data())  # Convert to BytesIO stream
        elif isinstance(image_data, bytes):  # If the image data is raw bytes
            return BytesIO(image_data)  # Convert to BytesIO stream
        return image_data  # Return original image data if no conversion is needed

    def _get_file_type(self):
        """Helper method to determine the file type based on the file loader used (pdf, docx, ppt)."""
        file_loader_mapping = {
            PDFLoader: 'pdf',
            DOCXLoader: 'docx',
            PPTLoader: 'ppt'
        }

        for loader_class, file_type in file_loader_mapping.items():
            if isinstance(self.extractor.file_loader, loader_class):
                return file_type  # Return file type based on the loader class

        return 'unknown'  # Default to 'unknown' if no match is found

    def close(self):
        """Close the database connection."""
        self.conn.close()