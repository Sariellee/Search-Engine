class Tree:
    """This class implements the prefix-tree index structure."""
    letter: str = None
    children: dict = {}
    terminal: bool = False

    def __init__(self, letter: str, terminal: bool = False) -> None:
        self.letter = letter
        self.children = {}
        self.terminal = terminal

    def get_child_words(self, word_part: str) -> list:
        """Returns a list of words, which start with 'word_part' argument."""
        cur = self
        self._child_words = []

        # parse the tree for a beginning of a word
        for letter in word_part:
            cur = cur.children.get(letter)
            if cur == None:
                # if the word_part is not in the tree, return nothing
                return []

        if cur.terminal:
            self._child_words.append(word_part)
        for _, child in cur.children.items():
            self._get_child_words_rec(child, word_part)
        return self._child_words

    def _get_child_words_rec(self, cur, word: str):
        if cur.terminal:
            self._child_words.append(word + cur.letter)
        for _, i in cur.children.items():
            self._get_child_words_rec(i, word + cur.letter)
