import fitz
import pymupdf
import sys
import re

pymupdf.TOOLS.mupdf_display_errors(False)
class FileReader:
    def __init__(self,file_path):
        self.path = file_path


    def get_content_as_string(self, start_page: int = 0):
        #print(f"page count is  {len(self.doc)}")
        doc = fitz.open(self.path)
        safe_start = max(0, min(start_page, len(doc)))
        book_content = " ".join([page.get_text() for page in doc[safe_start:]])
        first_split = re.split(r'(?<=[.!?])\s*', book_content)
        return first_split
