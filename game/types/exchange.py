import logging

from .player import Player
from ..exceptions import *
from config import *


class Exchange:
    def __init__(self, client: Player):
        self.client = client

    async def convert(self, from_currency: str, to_currency: str, value: float):
        all_currencies_balance = await self.client.balance.get_all_currencies_balance()
        from_currency_balance = all_currencies_balance[from_currency]
        print(from_currency_balance)
        if value > from_currency_balance:
            raise NotEnoughMoneyOnBalance(requested_value=value,
                                          available_value=from_currency_balance)
        converted_value = (value * CURRENCY_PRICES['main'] * CURRENCY_PRICES[to_currency]) / (CURRENCY_PRICES['main'] * CURRENCY_PRICES[from_currency])
        logging.info(f"convert from {from_currency} to {to_currency}; {value=}; {converted_value=}")
        await self.client.balance.add_money(to_currency, value)
        await self.client.balance.add_money(from_currency, -value)
