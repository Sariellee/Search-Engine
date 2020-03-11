from collections import Counter
import re

from crawler.html_document import HtmlDocument


class HtmlDocumentTextData:

    def __init__(self, url):
        self.doc = HtmlDocument(url)
        self.doc.get()
        self.doc.parse()

    def get_sentences(self):
        # TODO*: implement sentence parser
        return re.split('[.!?] ', self.doc.text)

    def get_word_stats(self):
        # TODO return Counter object of the document
        return Counter(self.doc.text.lower().split())