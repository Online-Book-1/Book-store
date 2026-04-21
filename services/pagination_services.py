 

from models.page import Page
from typing import List

class PaginationService:
    def __init__(self, num_of_words_per_page: int = 300):
        self.total_words = num_of_words_per_page

    def create_pages(self, text: str) -> List[Page]:
        words = text.split()
        pages = []
        for i in range(0, len(words), self.total_words):
            chunk    = " ".join(words[i: i + self.total_words])
            page_num = (i // self.total_words) + 1
            pages.append(Page(
    page_id    = f"Page_{page_num}",
    page_no    = page_num,
    content    = chunk
)) 
        return pages

