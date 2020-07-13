class BadRequest(Exception):
    def __init__(self, txt=None):
        self.txt = txt


class UserDoesNotExist(Exception):
    def __init__(self, txt=None):
        self.txt = txt


class SendermanRoulleteApiException(Exception):
    def __init__(self, txt=None):
        self.txt = txt
