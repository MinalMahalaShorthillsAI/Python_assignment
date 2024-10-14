from file_loader import PDFLoader, DOCXLoader, PPTLoader
from data_extractor import DataExtractor
from storage import Storage, StorageSQL

def process_file(loader_class, db_path, base_output_folder):
    extractor = DataExtractor(loader_class)
    sql_storage = StorageSQL(extractor, db_path)
    
    # Save data to SQL
    sql_storage.save_text()
    sql_storage.save_links()
    sql_storage.save_images()
    sql_storage.save_tables()
    sql_storage.close()

    # Save data to filesystem
    fs_storage = Storage(extractor, base_output_folder)
    fs_storage.save_text()
    fs_storage.save_links()
    fs_storage.save_images()
    fs_storage.save_tables()

def main():
    # Define file paths and output locations
    pdf_file = 'sample.pdf'
    docx_file = 'sample.docx'
    ppt_file = 'sample.pptx'
    base_output_folder = 'output_data'
    db_path = 'extracted_data.db'

    # Processing logic for PDF, DOCX, and PPT files
    process_file(PDFLoader(pdf_file), db_path, base_output_folder)
    process_file(DOCXLoader(docx_file), db_path, base_output_folder)
    process_file(PPTLoader(ppt_file), db_path, base_output_folder)

if __name__ == "__main__":
    main()
