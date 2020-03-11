import requests
from urllib.parse import quote


class Document:

    def __init__(self, url):
        self.url = url

    def get(self):
        if not self.load():
            if not self.download():
                raise FileNotFoundError(self.url)
            else:
                self.persist()

    def download(self):
        try:
            r = requests.get(self.url)  # , verify=False)
        except Exception as e:
            print(e)
            return False
        self.content = r.content
        return True

    def persist(self):
        self.download()
        with open(self.url.replace('/', ''), 'wb+') as f:
            f.write(self.content)
            f.close()
        return True

    def load(self):
        try:
            with open(self.url.replace('/', ''), 'rb') as f:
                self.content = f.read()
                return True
        except FileNotFoundError:
            return False
