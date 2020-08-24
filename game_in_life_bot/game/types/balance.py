from dataclasses import dataclass

from ... import config
from ...senderman_roullette_api import SendermanRoulletteApi
from ..exceptions import *


@dataclass
class AllCurrenciesBalance:
    main: float = 0.0
    pasyucoin: float = 0.0
    yulcoin: float = 0.0

    def __getitem__(self, item):
        return getattr(self, item)


class Balance:
    def __init__(self,
                 player: 'Player' = None):
        self.player: 'Player' = player

    @property
    def main_currency_balance(self) -> float:
        return self.player.model.main_currency_balance or 0.0

    @property
    def pasyucoin_currency_balance(self) -> float:
        # get value through API

        return 0.0

    @property
    async def yulcoin_currency_balance(self) -> float:
        async with SendermanRoulletteApi() as api:
            balance = await api.get_balance(self.player.tg_id)
        return float(balance) if balance else None

    async def get_all_currencies_balance(self) -> AllCurrenciesBalance:
        return AllCurrenciesBalance(main=self.main_currency_balance,
                                    pasyucoin=self.pasyucoin_currency_balance,
                                    yulcoin=await self.yulcoin_currency_balance)

    async def add_money_to_main_currency_balance(self, value: float):
        user = self.player.model
        user.inc_main_currency_balance(value)

    async def add_money_to_yulcoin_currency_balance(self, value: float):
        token = config.SENDERMAN_SECURE_API_BOT_TOKEN
        async with SendermanRoulletteApi(token) as api:
            await api.update_coins(self.player.tg_id, round(value))

    async def add_money(self, currency: str, value: float):
        if currency == 'main':
            await self.add_money_to_main_currency_balance(value)
        elif currency == 'yulcoin':
            await self.add_money_to_yulcoin_currency_balance(value)
        else:
            raise CurrencyDoesNotExist(currency)
