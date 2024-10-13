# Python_assignment
Overview
This project is a Python-based tool that extracts text, images, tables, and links from various file types: PDF, DOCX, and PPTX. The extracted data is saved into organized subfolders for each file type, ensuring easy access to the results.

The project uses an object-oriented approach where specific loaders handle each file type (PDFLoader, DOCXLoader, PPTLoader). The DataExtractor class extracts content from the files, and the Storage class saves the data into a structured folder system.

Features
PDF Extraction:

Extract text using pdfminer or fallback to OCR (pytesseract).
Extract hyperlinks and metadata from PDF annotations.
Extract embedded images and tables.
DOCX Extraction:

Extract text from Word documents.
Extract hyperlinks and embedded images.
Extract tables from DOCX files.
PPTX Extraction:

Extract text from PowerPoint slides.
Extract hyperlinks and embedded images.
Extract tables from PowerPoint presentations.
Storage: Saves the extracted data into organized folders:

Text files in the text folder.
Links in the links folder.
Images in the images folder.
Tables in the tables folder.
Project Structure
bash
Copy code
├── file_extractors.py        # Main script with file loaders, extractors, and storage logic
├── README.md                 # This README file
├── requirements.txt          # Required dependencies
├── test_files/               # Folder containing sample test files for validation
│   ├── sample.pdf
│   ├── sample.docx
│   ├── sample.pptx
├── test_output/              # Folder to store extracted data
└── test_file_extractors.py   # Unit tests for the project
Dependencies
pdfminer: Extracts text from PDF files.
pdfplumber: Extracts hyperlinks, images, and tables from PDFs.
docx: Loads and extracts data from DOCX files.
pptx: Loads and extracts data from PPTX files.
pdf2image: Converts PDF pages to images for OCR.
pytesseract: Performs OCR on images.
Pillow: Handles image processing and saving.
To install the required dependencies, run:

Copy code
pip install -r requirements.txt
Folder Structure for Extracted Data
The extracted data is saved in a base output folder with the following subfolders:

Text: Extracted text from the file is saved in text/<file_type>_text.txt.
Links: Extracted hyperlinks are saved in links/<file_type>_links.txt.
Images: Extracted images are saved in images/<file_type>_image_<index>.<extension>.
Tables: Extracted tables are saved as CSV files in tables/table_<file_type>_<index>.csv.
Usage
Running the Script
Place the input files (PDF, DOCX, PPTX) in the working directory.
Update the file paths in the script to point to the correct files.
Specify the output folder (base_output_folder) to store the extracted data.
Run the script to process the files.
Example Code Usage
After specifying the input file paths (e.g., pdf_file, docx_file, ppt_file), and setting the base output folder, the script will extract the data and save it in the specified folder.

For each file type (PDF, DOCX, PPTX), it will save:

The extracted text in the text folder.
The links in the links folder.
Images in the images folder.
Tables in the tables folder.
Example Output
After running the script, the following files will be created under the output_data folder:

text/pdf_text.txt: Contains the text extracted from the PDF file.
links/pdf_links.txt: Contains the hyperlinks found in the PDF.
images/pdf_image_1.png, pdf_image_2.jpg: Images extracted from the PDF.
tables/table_pdf_1.csv: Tables extracted from the PDF.
The same structure is followed for DOCX and PPTX files, with their respective text, links, images, and tables saved in the corresponding subfolders.

Unit Testing
Unit tests are available in the test_file_extractors.py file. These tests validate the loading and extraction logic for each file type and ensure that the output files are saved correctly.

To run the tests, use:

Copy code
python -m unittest test_file_extractors.py
Conclusion
This project efficiently extracts content from PDF, DOCX, and PPTX files, saving the extracted data in an organized manner. The modular design allows easy extension and customization for additional file types or extraction features.
