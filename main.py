from file_loader import PDFLoader, DOCXLoader, PPTLoader
from data_extractor import DataExtractor
from storage import Storage, StorageSQL

def process_file(loader_class, db_path, base_output_folder):
    """
    Process a file using the specified loader class, saving extracted data to both a database and the filesystem.

    Args:
        loader_class: An instance of a file loader (PDFLoader, DOCXLoader, or PPTLoader) initialized with the file path.
        db_path: The path to the SQLite database where data will be stored.
        base_output_folder: The folder path where extracted data will be saved to the filesystem.
    """
    # Create an instance of DataExtractor using the provided file loader
    extractor = DataExtractor(loader_class)
    
    # Initialize SQL storage for saving extracted data to a database
    sql_storage = StorageSQL(extractor, db_path)
    
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


def main():
    """
    Main function to define file paths and output locations, and initiate the processing of each file type.
    """
    # Define file paths for documents and output locations
    pdf_file = 'files/Document 2.pdf'
    docx_file = 'files/Document 2.docx'
    ppt_file = 'files/Document 2.pptx'
    base_output_folder = 'output_data'  # Output folder for extracted data
    db_path = 'extracted_data.db'        # Database path for storing extracted data

    # Process each file type by calling the process_file function with the appropriate loader
    process_file(PDFLoader(pdf_file), db_path, base_output_folder)
    process_file(DOCXLoader(docx_file), db_path, base_output_folder)
    process_file(PPTLoader(ppt_file), db_path, base_output_folder)

# Check if the script is being run directly and call the main function
if __name__ == "__main__":
    main()
