import logging
from aiohttp import ClientSession
from urlpath import URL

from .exceptions import *


class SendermanRoulletteApi:
    _base_url = URL('https://rouletteapi.herokuapp.com/users/')

    def __init__(self, bot_token: str = None, session: ClientSession = None):
        self._bot_token = bot_token
        self._session = session or ClientSession()

    async def get_balance(self, user_id: int):
        url = self._generate_url('getBalance', False, user_id=user_id)
        result = await self._session.get(url)
        result = await self._get_result_or_raise(result, 'getBalance', user_id=user_id)
        coins = result['coins']
        if coins == -1:
            raise UserDoesNotExist(str(user_id))
        return coins

    async def update_coins(self, user_id: int, coins: int):
        url = self._generate_url('updateCoins', True, user_id=user_id, coins=coins)
        print(url)
        result = await self._session.put(url)
        result = await self._get_result_or_raise(result, 'updateCoins', user_id=user_id, coins=coins)

    @classmethod
    async def _get_result_or_raise(cls,
                                   response,
                                   request_path,
                                   **kwargs):
        if response.status != 200:
            log = f'{request_path} request was unsuccessfull'
            for kwarg in kwargs:
                log += f' with {kwarg} {kwargs[kwarg]}'
            logging.error(log)
            raise BadRequest(response.status)
        result = await response.json()
        if result.get('ok') is False:
            raise SendermanRoulleteApiException(str(result))
        return result

    def _generate_url(self, path: str, needs_auth: bool = True, **kwargs):
        query = {k: v for k, v in kwargs.items()}
        if needs_auth:
            query.update({'token': self._bot_token})
        return str((self._base_url / path).add_query(query))

    async def disconnect(self):
        await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
