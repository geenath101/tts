import logging
import fitz
import pymupdf
import sys
import re

pymupdf.TOOLS.mupdf_display_errors(False)

logger = logging.getLogger(__name__)

class FileReader:
  
    def get_content_as_string(self, doc: fitz.Document, start_page: int = 0) -> list[str]:
        logger.debug(f"Loading page {start_page}")
        page = doc.load_page(start_page)
        logger.debug(f"Loading page {page.number}")
        safe_start = max(0, min(start_page, len(doc)))
        book_content = " ".join([page.get_text() for page in doc[safe_start:]])
        first_split = re.split(r'(?<=[.!?])\s*', book_content)
        logger.debug(f"Split into {len(first_split)} sentences")
        logger.debug(f"First 5 sentences: {first_split[:5]}")
        return first_split
