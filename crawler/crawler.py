from queue import Queue

from crawler.html_text_data import HtmlDocumentTextData


class Crawler:

    def crawl_generator(self, source, depth=1):
        queue = Queue()
        queue.put(source)

        cur_depth = 0
        while not queue.empty():
            try:
                page = HtmlDocumentTextData(queue.get())
                yield page
            except FileNotFoundError:
                continue
            if cur_depth < depth:
                cur_depth += 1
                anchors = page.doc.anchors
                [queue.put(anchor[1]) for anchor in anchors]