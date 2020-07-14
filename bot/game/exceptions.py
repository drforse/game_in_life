class CountryDoesntExistException(Exception):
    def __init__(self, txt):
        self.txt = txt


class ContentTypeUnexpected(Exception):
    def __init__(self, txt):
        self.txt = txt
