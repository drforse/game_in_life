class NotEnoughMoneyOnBalance(Exception):
    def __init__(self, txt: str = None, requested_value: float = None, available_value: float = None):
        self.txt = txt
        self.requested_value = requested_value
        self.available_value = available_value
        if not self.txt:
            self.txt = f"requested_value: {self.requested_value}; available_value: {self.available_value}"


class EffectTypeNotKnown(Exception):
    def __init__(self, txt: str = None):
        self.txt = txt


class NoItemInBuildpack(Exception):
    def __init__(self, txt: str = None):
        self.txt = txt


class CurrencyDoesNotExist(Exception):
    def __init__(self, txt: str = None):
        self.txt = txt


class ItemDoesNotExist(Exception):
    def __init__(self, txt: str = None):
        self.txt = txt


class NotEnoughItems(Exception):
    def __init__(self, txt: str = None):
        self.txt = txt
