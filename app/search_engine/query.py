import distance
from jellyfish import soundex

from app.search_engine.index import Indexes
from app.search_engine.preprocessing import Preprocessor


class QueryProcessor:
    def __init__(self):
        self._index = Indexes()
        self._preprocessor = Preprocessor()

    def _wildcard_search(self, tree_index, inv_tree_index, query):
        print(f"found asterisk in word {query}...")
        before = query[:query.index('*')]
        after = query[query.index('*') + 1:]
        print(f'before: "{before}"; after: "{after}"')
        # search first part in straight tree, second part in reversed tree
        # if one of the words is empty string (i.e. '*food'), then assign empty list
        before_words = tree_index.get_child_words(before) if before is not '' else list(self._index.index_keys())
        after_words = [result[::-1] for result in
                       inv_tree_index.get_child_words(after[::-1])] if after is not '' else list(
            self._index.index_keys())

        keyset = set(before_words) & set(after_words)
        print(f"found {len(keyset)} words matching wildcard query word: {keyset}")
        result = []
        for key in keyset:
            result.extend(self._index.get_from_index(key))

        return list(set(result))

    def search(self, query):
        query_words = self._preprocessor.preprocess(query)
        articles_for_each_word = []
        for word in query_words:
            if '*' in word:
                result = self._wildcard_search(self._index.tree_index, self._index.inv_tree_index, word)
                articles_for_each_word.append(result)
            else:
                # if query doesn't have '*' in it, we check query in index
                articles = self._index.get_from_index(word)
                if articles != None:
                    print(f"found {len(articles)} articles on word '{word}'")
                    # if word exists in the index
                    articles_for_each_word.append(articles)
                else:
                    print(f"did not find word '{word}' in index, trying soundex&levenshtein...")
                    # if word doesn't exist in the index, try soundex and levenshtein distance
                    soundex_words = self._index.soundex_index.get(soundex(word))
                    if soundex_words:
                        # limit words by levenshtein distance (3 is chosen arbitrarily)
                        soundex_words = list(
                            filter(lambda i: distance.levenshtein(word, i) < 3 and i in self._index.index_keys(),
                                   soundex_words))
                        print(
                            f"found {len(soundex_words)} words that matched levenshtein distance with '{word}'': {soundex_words}")
                        [articles_for_each_word.append(self._index.get_from_index(soundex_word)) for soundex_word in
                         soundex_words]
                        print(f"found {len(articles_for_each_word)} aticles on query {query}")

        if len(articles_for_each_word) == 0:
            # no articles were found
            return []
        elif len(articles_for_each_word) == 1:
            # if only one word in query OR if only one word from query is in index
            return list(set(articles_for_each_word[0]))
        else:
            return list(set(articles_for_each_word[0]).union(*articles_for_each_word))
