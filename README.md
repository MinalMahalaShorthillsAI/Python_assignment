###Data Extraction Project
This project extracts text, hyperlinks, images, tables, and metadata from various file formats (PDF, DOCX, and PPT). It provides a modular architecture that supports storing extracted data in the file system or MySQL databases, making it highly adaptable for various use cases.

###Features
##Extraction Capabilities:

Text: Extracts plain text content from supported file formats.
Hyperlinks: Captures and stores all hyperlinks present in the documents.
Images: Extracts and saves embedded images.
Tables: Extracts tabular data and saves it in CSV format.
Metadata: Extracts and stores metadata associated with the documents (e.g., author, creation date).

##Supported File Formats:

PDF
DOCX
PPT

##Storage Options:

Saves extracted data locally in structured directories (text, images, links, tables, and metadata).
Supports saving extracted data into a MySQL database for easy querying and management.

##Requirements

To run this project, you will need:

Python 3.x

##Libraries:

Pillow (PIL) for image processing
mysql-connector-python for MySQL operations
csv for handling CSV file formats
os for file and directory operations

###Installation

Clone the Repository:

git clone https://github.com/your-username/data-extraction-project.git
cd data-extraction-project

Install Required Libraries:

pip install -r requirements.txt
Set Up a Virtual Environment (Optional but recommended):

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

##Usage

Prepare your Files: Ensure your target files (PDF, DOCX, or PPT) are ready for extraction.
Run the Extraction: Run the main.py script with the required file path and output configuration.

python main.py
View Extracted Data: Use the built-in method display_data to view the extracted data stored in the MySQL database.

Example Workflow

Run the Script:

python main.py --file-path /path/to/your/file.pdf --output-type sql
View Extracted Data (MySQL storage example):

python main.py --action display --file-type pdf

###Project Structure

├── main.py               # Main script to run the extraction process
├── data_extractor.py      # Extractor class for extracting data from files
├── file_loader.py         # Classes for loading PDF, DOCX, and PPT files
├── storage.py             # Storage classes for saving data to file system or MySQL
├── requirements.txt       # List of dependencies
└── README.md              # This documentation file

##Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

##Fork the repository.

Create a new branch for your feature/bug fix.
Commit your changes and open a pull request.
Make sure to include tests and update documentation where necessary.