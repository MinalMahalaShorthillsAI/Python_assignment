from file_loader import PDFLoader, DOCXLoader, PPTLoader
from data_extractor import DataExtractor
from storage import Storage, StorageSQL
import os
from __init__ import db_config

def process_file(loader_class, db_config, base_output_folder):
    """
    Process a file using the specified loader class, saving extracted data to both a database and the filesystem.

    Args:
        loader_class: An instance of a file loader (PDFLoader, DOCXLoader, or PPTLoader) initialized with the file path.
        db_config: A dictionary containing MySQL database configuration.
        base_output_folder: The folder path where extracted data will be saved to the filesystem.
    """
    # Create an instance of DataExtractor using the provided file loader
    extractor = DataExtractor(loader_class)
    
    # Initialize SQL storage for saving extracted data to a database
    sql_storage = StorageSQL(extractor, db_config)  # Pass db_config instead of db_path
    
    # Save various types of extracted data to the SQL database
    sql_storage.save_text()          # Save extracted text data
    sql_storage.save_links()         # Save extracted hyperlinks
    sql_storage.save_images()        # Save extracted images
    sql_storage.save_tables()        # Save extracted tables
    sql_storage.save_metadata()      # Save metadata about the extracted content
    sql_storage.close()              # Close the database connection

    # Initialize filesystem storage for saving extracted data to the local filesystem
    fs_storage = Storage(extractor, base_output_folder)
    
    # Save various types of extracted data to the filesystem
    fs_storage.save_text()          # Save extracted text data
    fs_storage.save_links()         # Save extracted hyperlinks
    fs_storage.save_images()        # Save extracted images
    fs_storage.save_tables()        # Save extracted tables
    fs_storage.save_metadata()      # Save metadata about the extracted content

def get_file_path(prompt):
    """Prompt the user for a file path and check if it exists."""
    while True:
        file_path = input(prompt)
        if os.path.isfile(file_path):
            return file_path
        else:
            print("File not found. Please provide a valid file path.")

def request_files():
    """Request necessary files from the user until all are provided."""
    required_files = {
        'pdf': None,
        'docx': None,
        'ppt': None
    }

    for file_type in required_files.keys():
        required_files[file_type] = get_file_path(f"Please provide the path for the {file_type.upper()} file: ")

    print("All required files have been provided.")
    return required_files

def main():
    # Request files from the user
    files = request_files()
    
    # Print the collected file paths
    print("\nYou provided the following files:")
    for file_type, file_path in files.items():
        print(f"{file_type.upper()}: {file_path}")

    # Define the base output folder
    base_output_folder = 'output_folder'  # Change this as needed

    # Process each file type by calling the process_file function with the appropriate loader
    process_file(PDFLoader(files['pdf']), db_config, base_output_folder)
    process_file(DOCXLoader(files['docx']), db_config, base_output_folder)
    process_file(PPTLoader(files['ppt']), db_config, base_output_folder)

# Check if the script is being run directly and call the main function
if __name__ == "__main__":
    main()
