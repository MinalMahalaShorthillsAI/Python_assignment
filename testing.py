import os
import unittest
from unittest.mock import patch, MagicMock
from extractor import PDFLoader, DOCXLoader, PPTLoader, DataExtractor, Storage


class TestFileExtractors(unittest.TestCase):
    def setUp(self):
        # Setup paths for testing (These files should exist for testing)
        self.test_pdf = 'test_files/sample.pdf'
        self.test_docx = 'test_files/sample.docx'
        self.test_pptx = 'test_files/sample.pptx'
        self.base_output_folder = 'test_output'

        # Ensure the output directory is empty before each test
        if os.path.exists(self.base_output_folder):
            for filename in os.listdir(self.base_output_folder):
                file_path = os.path.join(self.base_output_folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    def test_pdf_loader(self):
        pdf_loader = PDFLoader(self.test_pdf)
        self.assertTrue(pdf_loader.validate_file())
        content = pdf_loader.load_file()
        self.assertIsInstance(content, str)  # Assuming the PDF text is returned as a string
        links = pdf_loader.extract_links()
        self.assertIsInstance(links, list)
        images = pdf_loader.extract_images()
        self.assertIsInstance(images, list)
        tables = pdf_loader.extract_tables()
        self.assertIsInstance(tables, list)

    def test_docx_loader(self):
        docx_loader = DOCXLoader(self.test_docx)
        self.assertTrue(docx_loader.validate_file())
        content = docx_loader.load_file()
        self.assertIsInstance(content, Document)
        text = DataExtractor(docx_loader).extract_text()
        self.assertIsInstance(text, str)

    def test_ppt_loader(self):
        ppt_loader = PPTLoader(self.test_pptx)
        self.assertTrue(ppt_loader.validate_file())
        content = ppt_loader.load_file()
        self.assertIsInstance(content, Presentation)
        text = DataExtractor(ppt_loader).extract_text()
        self.assertIsInstance(text, str)

    def test_data_extractor(self):
        pdf_loader = PDFLoader(self.test_pdf)
        data_extractor = DataExtractor(pdf_loader)
        self.assertTrue(data_extractor.extract_text())
        self.assertTrue(data_extractor.extract_links())
        self.assertTrue(data_extractor.extract_images())
        self.assertTrue(data_extractor.extract_tables())

    def test_storage_saves_files(self):
        pdf_loader = PDFLoader(self.test_pdf)
        data_extractor = DataExtractor(pdf_loader)
        storage = Storage(data_extractor, self.base_output_folder)

        storage.save_text()
        storage.save_links()
        storage.save_images()
        storage.save_tables()

        # Check if text file is created
        text_file_path = os.path.join(self.base_output_folder, 'text', 'pdf_text.txt')
        self.assertTrue(os.path.exists(text_file_path))

        # Check if links file is created
        links_file_path = os.path.join(self.base_output_folder, 'links', 'pdf_links.txt')
        self.assertTrue(os.path.exists(links_file_path))

        # Check if images are saved
        images_folder_path = os.path.join(self.base_output_folder, 'images')
        self.assertTrue(len(os.listdir(images_folder_path)) > 0)

        # Check if tables are saved
        tables_folder_path = os.path.join(self.base_output_folder, 'tables')
        self.assertTrue(len(os.listdir(tables_folder_path)) > 0)

    def test_invalid_pdf(self):
        invalid_loader = PDFLoader('invalid_file.pdf')
        self.assertFalse(invalid_loader.validate_file())
        with self.assertRaises(ValueError):
            invalid_loader.load_file()

    def test_invalid_docx(self):
        invalid_loader = DOCXLoader('invalid_file.docx')
        self.assertFalse(invalid_loader.validate_file())
        with self.assertRaises(ValueError):
            invalid_loader.load_file()

    def test_invalid_pptx(self):
        invalid_loader = PPTLoader('invalid_file.pptx')
        self.assertFalse(invalid_loader.validate_file())
        with self.assertRaises(ValueError):
            invalid_loader.load_file()

    def test_edge_case_empty_pdf(self):
        empty_pdf_loader = PDFLoader('test_files/empty.pdf')  # Ensure this file is empty
        self.assertTrue(empty_pdf_loader.validate_file())
        content = empty_pdf_loader.load_file()
        self.assertEqual(content.strip(), "")  # Expecting empty string

    def test_edge_case_no_links_docx(self):
        docx_loader = DOCXLoader('test_files/no_links.docx')  # Ensure this file has no links
        self.assertTrue(docx_loader.validate_file())
        data_extractor = DataExtractor(docx_loader)
        links = data_extractor.extract_links()
        self.assertEqual(links, [])

    def test_edge_case_no_images_pptx(self):
        ppt_loader = PPTLoader('test_files/no_images.pptx')  # Ensure this file has no images
        self.assertTrue(ppt_loader.validate_file())
        data_extractor = DataExtractor(ppt_loader)
        images = data_extractor.extract_images()
        self.assertEqual(images, [])

    def tearDown(self):
        # Clean up the output directory after tests
        if os.path.exists(self.base_output_folder):
            for filename in os.listdir(self.base_output_folder):
                file_path = os.path.join(self.base_output_folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

if __name__ == "__main__":
    unittest.main()
