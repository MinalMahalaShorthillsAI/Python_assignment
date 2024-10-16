Overview
--------
This project extracts text, links, images, tables, and metadata from various file formats, including PDF, DOCX, and PPT. It provides a modular architecture that supports both file system storage and SQLite database storage for extracted data.

Features
--------
Extracts and saves:
--------
Text content from files
Hyperlinks from documents
Images embedded in files
Tables in CSV format
Metadata associated with files

Supports three file formats:
--------
PDF
DOCX
PPT

Data storage options:
--------
Saves extracted data to the file system
Stores extracted data in an SQLite database
Displays stored data from the database
--------

Requirements
--------
Python 3.x
Libraries:
PIL (Pillow) for image processing
sqlite3 for database operations
csv for handling CSV files
os for file and directory operations
--------

Installation
--------
Clone this repository to your local machine.
Navigate to the project directory.
Install the required libraries using pip:
pip install pillow

Set up a virtual environment.
--------
Usage
--------
Prepare your files (PDF, DOCX, PPT) that you want to extract data from.
Run the main script with the desired file path and output configuration.

Example command: python main.py
Use the display_data method to view the data stored in the SQLite database.

Project Structure
--------------------------------------------------------------------------------------------------------
main.py: The main script to run the extraction process.
data_extractor.py: Contains the DataExtractor class responsible for extracting data from files.
file_loader.py: Contains classes for loading different file types (PDFLoader, DOCXLoader, PPTLoader).
storage.py: Contains classes for saving extracted data (Storage and StorageSQL).
README.md: This documentation file.
---------------------------------------------------------------------------------------------------------

Contributing
-------
Contributions are welcome! If you'd like to contribute to this project, please fork the repository and submit a pull request.

