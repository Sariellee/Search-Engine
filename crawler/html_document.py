from bs4 import BeautifulSoup
from bs4.element import Comment
from urllib.parse import urljoin, urlsplit

from crawler.document import Document


class HtmlDocument(Document):

    def parse(self):
        # TODO exctact plain text, images and links from the document
        soup = BeautifulSoup(self.content)
        self.anchors = self._get_links(soup)
        self.images = self._get_images(soup)
        self.text = self._get_text(soup)

    def _get_links(self, soup):
        links = []
        for link in soup.find_all('a', href=True):
            if link.get('href') and link['href'].startswith('http'):
                # if absolute url, just include it
                links.append((link.text, link['href']))
            elif link['href'].startswith('/'):
                # if relative url, get the base url and add relative url to it
                url = urljoin(f"{urlsplit(self.url).scheme}://{urlsplit(self.url).hostname}", link['href'])
                links.append((link.text, url))

        return links

    def _get_images(self, soup):
        links = []
        for link in soup.find_all("img"):
            if not link.get('src'):
                continue
            if link['src'].startswith('http'):
                links.append(link['src'])
            else:
                url = urljoin(f"{urlsplit(self.url).scheme}://{urlsplit(self.url).hostname}", link['src'])
                links.append(url)
        return links

    def tag_visible(self, element):
        # taken from https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text/1983219#1983219
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def _get_text(self, soup):
        # taken from https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text/1983219#1983219
        texts = soup.findAll(text=True)
        visible_texts = filter(self.tag_visible, texts)
        return u" ".join(t.strip() for t in visible_texts)
