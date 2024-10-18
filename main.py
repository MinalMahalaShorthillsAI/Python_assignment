import os
from file_loader import PDFLoader, DOCXLoader, PPTLoader  # Import your file loaders
from data_extractor import DataExtractor
from storage import Storage, StorageSQL
from __init__ import db_config

def process_file(file_loader_class, db_config, base_output_folder):
    """
    Process a file using the specified loader class, saving extracted data to both a database and the filesystem.

    Args:
        file_loader_class: A file loader instance (PDFLoader, DOCXLoader, or PPTLoader).
        db_config: A dictionary containing MySQL database configuration.
        base_output_folder: The folder path where extracted data will be saved to the filesystem.
    """
    try:
        # Load the file using the provided file loader class
        loaded_file = file_loader_class.load_file()  # Load the file

        # Create an instance of DataExtractor with the file loader
        extractor = DataExtractor(file_loader_class)  # Pass the loader class instance
        extractor.content = loaded_file  # Set the content after loading the file

        # Initialize SQL storage
        sql_storage = StorageSQL(extractor, db_config)
        # Save extracted data to SQL database
        sql_storage.save_text()
        sql_storage.save_links()
        sql_storage.save_images()
        sql_storage.save_tables()
        sql_storage.save_metadata()
        sql_storage.close()  # Close the database connection

        # Initialize filesystem storage
        fs_storage = Storage(extractor, base_output_folder)
        # Save extracted data to filesystem
        fs_storage.save_text()
        fs_storage.save_links()
        fs_storage.save_images()
        fs_storage.save_tables()
        fs_storage.save_metadata()

    except ValueError as e:
        print(f"Error processing file: {e}")

def main():
    """Main function to execute the program."""
    # Collect file paths directly from user input
    pdf_file_path = input("Please provide the path for the PDF file: ")
    docx_file_path = input("Please provide the path for the DOCX file: ")
    ppt_file_path = input("Please provide the path for the PPTX file: ")

    # Define the base output folder
    base_output_folder = 'output_folder'  # Change this as needed

    # Process each file type using the respective loader
    if os.path.isfile(pdf_file_path):
        process_file(PDFLoader(pdf_file_path), db_config, base_output_folder)
    else:
        print("Invalid PDF file path.")

    if os.path.isfile(docx_file_path):
        process_file(DOCXLoader(docx_file_path), db_config, base_output_folder)
    else:
        print("Invalid DOCX file path.")

    if os.path.isfile(ppt_file_path):
        process_file(PPTLoader(ppt_file_path), db_config, base_output_folder)
    else:
        print("Invalid PPTX file path.")

# Check if the script is being run directly and call the main function
if __name__ == "__main__":
    main()
