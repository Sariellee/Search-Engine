from urllib import request
from jellyfish import soundex
import os
from bs4 import BeautifulSoup
import shelve

from app.config import COLLECTION_SHELVE_PATH, COLLECTION_FULL_SHELVE_PATH, INDEX_SHELVE_PATH
from app.search_engine.preprocessing import Preprocessor
from app.search_engine.tree_index import Tree


class Indexes:
    def __init__(self):
        self._get_collection()
        self._make_index()
        self.tree_index = self._make_tree_index()
        self.inv_tree_index = self._make_tree_index(inverse=True)
        self.soundex_index = self._make_soundex_index()

    def get_from_index(self, key):
        with shelve.open(INDEX_SHELVE_PATH) as index:
            return index[key]

    def get_from_collection(self, key):
        with shelve.open(COLLECTION_SHELVE_PATH) as collection:
            return collection[key]

    def get_from_full_collection(self, key):
        with shelve.open(COLLECTION_FULL_SHELVE_PATH) as collection_full:
            return collection_full[key]

    def index_keys(self):
        with shelve.open(INDEX_SHELVE_PATH) as index:
            return list(index.keys())

    def _get_collection(self):
        collection = shelve.open(COLLECTION_SHELVE_PATH)
        collection_full = shelve.open(COLLECTION_FULL_SHELVE_PATH)
        if os.path.exists(COLLECTION_SHELVE_PATH) and os.path.exists(COLLECTION_FULL_SHELVE_PATH):
            print('collection already in place, skipping...')
            return
        preprocessor = Preprocessor()
        url = "https://archive.ics.uci.edu/ml/machine-learning-databases/reuters21578-mld/reuters21578.tar.gz"
        request.urlretrieve(url, 'reuters.tar.gz')
        os.makedirs('reuters', exist_ok=True)
        os.system('tar -C reuters -xf reuters.tar.gz')

        print(
            f"collecting articles from {len(list(filter(lambda i: i.startswith('reut'), os.listdir('reuters'))))} files")
        counter = 1
        for article in filter(lambda i: i.startswith('reut'), os.listdir('reuters')):
            with open(os.path.join('reuters', article)) as f:
                try:
                    soup = BeautifulSoup(f)
                    for i in soup.find_all('reuters'):
                        title = i.find('title')
                        if title is not None:
                            title = title.get_text()
                        else:
                            # if article has no title, take 40 first symbols of text and add '...' to it
                            title = i.find('text').get_text()[:40] + '...'
                        text = i.get_text()
                        collection[title] = preprocessor.preprocess(text)
                        collection_full[title] = text
                    print(f'Done: {counter} file')
                    counter += 1
                except UnicodeDecodeError as e:
                    print(f'Failed to process file {article}: {e}. Skipping..')
                    continue
        print("Done scanning files")
        collection.close()
        collection_full.close()

    def _make_index(self):
        if os.path.exists(INDEX_SHELVE_PATH) and os.path.exists(COLLECTION_SHELVE_PATH):
            print('index aleady in place, skipping...')
            return

        collection = shelve.open(COLLECTION_SHELVE_PATH)
        inverted_index = shelve.open(INDEX_SHELVE_PATH)

        i = 0
        for article_title, article_words in collection.items():
            i += 1
            for word in article_words:
                if inverted_index.get(word):
                    if article_title not in inverted_index[word]:
                        # if article not already added to index
                        article_titles = inverted_index[word]
                        article_titles.append(article_title)
                        inverted_index[word] = article_titles
                else:
                    inverted_index[word] = [article_title]
            if i % 100 == 0:
                print(f'DONE {i} / {len(collection)}')
                inverted_index.sync()
        collection.close()
        inverted_index.close()

    def _make_tree_index(self, inverse=False):
        """Create tree or inverse-tree index"""
        print(f'building{" inverted " if inverse else " "}tree index')
        collection = shelve.open(COLLECTION_SHELVE_PATH)
        tree_index = Tree(None)
        for _, article_words in collection.items():
            for word in article_words:
                cur_node = tree_index
                for letter in word if not inverse else word[::-1]:
                    if letter in cur_node.children:
                        cur_node = cur_node.children[letter]
                    else:
                        cur_node.children[letter] = Tree(letter)
                        cur_node = cur_node.children[letter]
                cur_node.terminal = True
        collection.close()
        return tree_index

    def _make_soundex_index(self):
        print('building soundex')
        """Creates a soundex index based on the collection's words."""
        collection = shelve.open(COLLECTION_SHELVE_PATH)
        soundex_index = {}
        for _, article_words in collection.items():
            for word in article_words:
                soundex_word = soundex(word)
                if soundex_word not in soundex_index.keys():
                    soundex_index[soundex_word] = [word]
                else:
                    if word not in soundex_index[soundex_word]:
                        soundex_index[soundex_word].append(word)
        collection.close()
        return soundex_index
