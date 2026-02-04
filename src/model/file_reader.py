import fitz
import pymupdf
import sys
import re

pymupdf.TOOLS.mupdf_display_errors(False)
class FileReader:
    def __init__(self,file_path):
        self.path = file_path


    def get_content_as_string(self):
        #print(f"page count is  {len(self.doc)}")
        doc = fitz.open(self.path)
        book_content =  " ".join([page.get_text() for page in doc])
        first_split = re.split(r'(?<=[.!?])\s*', book_content)
        return first_split
