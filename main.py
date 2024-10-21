import os
from file_loader import PDFLoader, DOCXLoader, PPTLoader  # Import your file loaders
from data_extractor import DataExtractor
from storage import Storage, StorageSQL
from __init__ import db_config

def process_file(file_loader, db_config, base_output_folder):
    """
    Process a file using the specified loader instance, saving extracted data to both a database and the filesystem.

    Args:
        file_loader: A file loader instance (PDFLoader, DOCXLoader, or PPTLoader).
        db_config: A dictionary containing MySQL database configuration.
        base_output_folder: The folder path where extracted data will be saved to the filesystem.
    """
    try:
        # Validate and load the file
        loaded_file = file_loader.validate_and_load_file()

        # Create an instance of DataExtractor with the file loader
        extractor = DataExtractor(file_loader)
        extractor.content = loaded_file  # Set the content after loading the file

        # Initialize SQL storage and save extracted data
        sql_storage = StorageSQL(extractor, db_config)
        save_extracted_data(sql_storage)

        # Initialize filesystem storage and save extracted data
        fs_storage = Storage(extractor, base_output_folder)
        save_extracted_data(fs_storage)

    except ValueError as e:
        print(f"Error processing file: {e}")

def save_extracted_data(storage):
    """Save extracted data to the provided storage instance."""
    storage.save_text()
    storage.save_links()
    storage.save_images()
    storage.save_tables()
    storage.save_metadata()
    
    if isinstance(storage, StorageSQL):
        storage.close()  # Close the database connection for SQL storage

def main():
    """Main function to execute the program."""
    # Define the base output folder
    base_output_folder = 'output_folder'  # Change this as needed

    # Create a dictionary to map file types to their loader classes and user prompts
    file_loaders = {
        'PDF': (PDFLoader, "Please provide the path for the PDF file: "),
        'DOCX': (DOCXLoader, "Please provide the path for the DOCX file: "),
        'PPTX': (PPTLoader, "Please provide the path for the PPTX file: ")
    }

    for file_type, (loader_class, prompt) in file_loaders.items():
        file_path = input(prompt)
        if os.path.isfile(file_path):
            process_file(loader_class(file_path), db_config, base_output_folder)
        else:
            print(f"Invalid {file_type} file path.")

# Check if the script is being run directly and call the main function
if __name__ == "__main__":
    main()
