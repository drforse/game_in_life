class NotEnoughMoneyOnBalance(Exception):
    def __init__(self, txt: str = None, requested_value: float = None, available_value: float = None):
        self.txt = txt
        self.requested_value = requested_value
        self.available_value = available_value
        if not self.txt:
            self.txt = f"requested_value: {self.requested_value}; available_value: {self.available_value}"
