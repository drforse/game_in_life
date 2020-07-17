class BadRequest(Exception):
    def __init__(self, txt=None):
        self.txt = txt


class UserNotFound(Exception):
    def __init__(self, txt=None):
        self.txt = txt


class Unauthorized(Exception):
    def __init__(self, txt=None):
        self.txt = txt


class NotEnoughCoinsRemaining(Exception):
    def __init__(self, txt=None):
        self.txt = txt


class SendermanRoulleteApiException(Exception):
    def __init__(self, txt=None):
        self.txt = txt
