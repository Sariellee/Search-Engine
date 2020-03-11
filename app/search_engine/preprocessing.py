import re

import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('punkt')


class Preprocessor:
    def _normalize(self, text):
        text = text.lower()  # lowering
        text = re.sub(r'[^A-Za-z*\s]', '', text).replace('  ', ' ')
        return text

    def _tokenize(self, text):
        return nltk.word_tokenize(text)

    def _get_wordnet_pos(self, word):
        """get word's part of speech"""
        # taken from https://webdevblog.ru/podhody-lemmatizacii-s-primerami-v-python/
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}
        return tag_dict.get(tag, wordnet.NOUN)

    def _lemmatization(self, tokens):
        lemmatizer = WordNetLemmatizer()
        return [lemmatizer.lemmatize(token, self._get_wordnet_pos(token)) for token in tokens]

    def _remove_stop_word(self, tokens):
        stop_words = set(stopwords.words('english'))
        return list(filter(lambda token: token not in stop_words, tokens))

    def preprocess(self, text):
        return self._remove_stop_word(self._lemmatization(self._tokenize(self._normalize(text))))
