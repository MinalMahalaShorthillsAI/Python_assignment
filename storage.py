import os
import csv
from io import BytesIO
import mysql.connector
from PIL import Image
from data_extractor import DataExtractor
from file_loader import PDFLoader, DOCXLoader, PPTLoader

# Storage class for saving extracted content to file system (local storage)
class Storage:
    def __init__(self, extractor: DataExtractor, base_path: str):
        self.extractor = extractor  # DataExtractor instance to extract content
        self.base_path = base_path  # Base directory path to store files
        self.ensure_directories_exist()  # Ensure necessary directories are created

    def ensure_directories_exist(self):
        """Create directories for saving images, tables, text, and links if they don't exist."""
        os.makedirs(os.path.join(self.base_path, 'images'), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, 'tables'), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, 'text'), exist_ok=True)
        os.makedirs(os.path.join(self.base_path, 'links'), exist_ok=True)

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
        self._save_to_file('links', 'links', lambda: self.extractor.extract_links(), format_func=str)

    def save_images(self):
        """Extract and save images to individual files."""
        images = self.extractor.extract_images()  # Get extracted images
        image_folder = os.path.join(self.base_path, 'images')  # Directory to save images
        file_type_prefix = self._get_file_type()  # Get file type for prefix

        for idx, image_data in enumerate(images):
            try:
                image_data = self._prepare_image_data(image_data)  # Prepare image data for saving
                image = Image.open(image_data)  # Open image using PIL
                image_path = os.path.join(image_folder, f'{file_type_prefix}_image_{idx + 1}.{image.format.lower()}')  # Set image path
                image.save(image_path)  # Save image
                print(f"Successfully saved image {idx + 1} to {image_path}")
            except Exception as e:
                print(f"Error saving image {idx + 1}: {e}")  # Handle image save errors

    def save_tables(self):
        """Extract and save tables in CSV format."""
        tables = self.extractor.extract_tables()  # Get extracted tables
        file_type = self._get_file_type()  # Get file type (e.g., pdf, docx)
        table_folder = os.path.join(self.base_path, 'tables')  # Directory to save tables

        for idx, table in enumerate(tables):
            csv_path = os.path.join(table_folder, f'table_{file_type}_{idx + 1}.csv')  # Set CSV file path
            self._write_csv(csv_path, table)  # Write table data to CSV

    def save_metadata(self):
        """Extract and save metadata to a file."""
        metadata = self.extractor.extract_metadata()  # Get extracted metadata
        metadata_folder = os.path.join(self.base_path, 'metadata')  # Directory to save metadata
        os.makedirs(metadata_folder, exist_ok=True)
        metadata_file = os.path.join(metadata_folder, f'{self._get_file_type()}_metadata.txt')  # File path for metadata

        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                for key, value in metadata.items():
                    f.write(f"{key}: {value}\n")  # Write metadata key-value pairs to file
            print(f"Successfully saved metadata to {metadata_file}")
        except Exception as e:
            print(f"Error saving metadata: {e}")  # Handle errors in saving metadata

    def _save_to_file(self, folder_name, file_type, extract_func, format_func=lambda x: x):
        """General method to save extracted data (e.g., links) to a file."""
        data = extract_func()  # Extract data using the provided function
        file_path = os.path.join(self.base_path, folder_name, f'{self._get_file_type()}_{folder_name}.txt')  # File path

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(f"{format_func(item)}\n")  # Write each item to the file
            print(f"Successfully saved {folder_name} to {file_path}")
        except Exception as e:
            print(f"Error saving {folder_name}: {e}")  # Handle errors in saving

    def _write_csv(self, file_path, data):
        """Helper method to write table data to a CSV file."""
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)  # Initialize CSV writer
                writer.writerows(data)  # Write rows to CSV file
            print(f"Successfully saved table to {file_path}")
        except Exception as e:
            print(f"Error saving table: {e}")  # Handle CSV save errors

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


# StorageSQL class for saving extracted content to a MySQL database
class StorageSQL:
    def __init__(self, extractor: DataExtractor, db_config):
        self.extractor = extractor  # DataExtractor instance to extract content
        self.conn = mysql.connector.connect(**db_config)  # Establish database connection using provided config
        self.create_tables()  # Ensure necessary tables are created

    def create_tables(self):
        """Create tables in the MySQL database for storing text, links, images, tables, and metadata."""
        cursor = self.conn.cursor()  # Create a cursor for executing SQL queries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_text (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_type VARCHAR(255),
                content TEXT
            )
        ''')  # Create table for storing extracted text
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_links (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_type VARCHAR(255),
                link TEXT
            )
        ''')  # Create table for storing extracted links
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_images (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_type VARCHAR(255),
                image LONGBLOB
            )
        ''')  # Create table for storing extracted images
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_tables (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_type VARCHAR(255),
                table_data TEXT
            )
        ''')  # Create table for storing extracted tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_metadata (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_type VARCHAR(255),
                `key` VARCHAR(255),
                `value` TEXT
            )
        ''')  # Create table for storing extracted metadata
        self.conn.commit()  # Commit the changes to the database

    def save_text(self):
        """Extract and save text to the database."""
        self._save_to_db('extracted_text', 'content', self.extractor.extract_text)

    def save_links(self):
        """Extract and save links to the database."""
        self._save_to_db('extracted_links', 'link', lambda: self.extractor.extract_links(), is_link=True)

    def save_images(self):
        """Extract and save images to the database."""
        images = self.extractor.extract_images()  # Get extracted images
        file_type = self._get_file_type()  # Get file type (e.g., pdf, docx)

        cursor = self.conn.cursor()  # Create a cursor for executing SQL queries
        for idx, image_data in enumerate(images):
            try:
                image_data = self._prepare_image_data(image_data)  # Prepare image data for saving
                img_byte_arr = self._get_image_bytes(image_data)  # Convert image to binary

                cursor.execute('''
                    INSERT INTO extracted_images (file_type, image)
                    VALUES (%s, %s)
                ''', (file_type, img_byte_arr))  # Insert image data into the database

            except Exception as e:
                print(f"Error saving image {idx + 1}: {e}")  # Handle image save errors

        self.conn.commit()  # Commit the changes to the database
        print("Image data saved to database.")

    def save_metadata(self):
        """Extract and save metadata to the database."""
        metadata = self.extractor.extract_metadata()  # Get extracted metadata
        file_type = self._get_file_type()  # Get file type (e.g., pdf, docx)
        cursor = self.conn.cursor()  # Create a cursor for executing SQL queries

        for key, value in metadata.items():
            cursor.execute('''
                INSERT INTO extracted_metadata (file_type, `key`, `value`)
                VALUES (%s, %s, %s)
            ''', (file_type, key, value))  # Insert metadata key-value pair into the database

        self.conn.commit()  # Commit the changes to the database
        print("Metadata saved to database.")

    def _save_to_db(self, table_name, column_name, extract_func, is_link=False):
        """General method to save extracted data (e.g., text, links) to the database."""
        data = extract_func()  # Extract data using the provided function
        file_type = self._get_file_type()  # Get file type (e.g., pdf, docx)

        cursor = self.conn.cursor()  # Create a cursor for executing SQL queries
        for item in data:
            if is_link and isinstance(item, tuple):
                item = item[1]  # Save only the hyperlink part if extracting links
            cursor.execute(f'''
                INSERT INTO {table_name} (file_type, {column_name})
                VALUES (%s, %s)
            ''', (file_type, item))  # Insert data into the database

        self.conn.commit()  # Commit the changes to the database
        print(f"{column_name.capitalize()} data saved to database.")

    def save_tables(self):
        """Extract and save tables to the database."""
        tables = self.extractor.extract_tables()  # Get extracted tables
        file_type = self._get_file_type()  # Get file type (e.g., pdf, docx)

        cursor = self.conn.cursor()  # Create a cursor for executing SQL queries
        for idx, table in enumerate(tables):
            # Convert None values in the table data to empty strings
            table_data = '\n'.join([','.join(str(item) if item is not None else '' for item in row) for row in table])

            cursor.execute('''
                INSERT INTO extracted_tables (file_type, table_data)
                VALUES (%s, %s)
            ''', (file_type, table_data))  # Insert table data into the database

        self.conn.commit()  # Commit the changes to the database
        print("Table data saved to database.")

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
