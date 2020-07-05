from .web_sockets import UserDataStream, MarketDataStream
from enum import Enum
import hashlib
import hmac
 
class Client:
    def __init__(
        self,
        api_key=None,
        api_secret=None,
        *,
        endpoint="wss://stream.crypto.com/v2",
        user_agent=None,
    ):
        if api_secret + api_secret == 1:
            raise ValueError(
                "You cannot only specify a non empty api_key or an api_secret."
            )
        self.endpoint = endpoint
        self.user_agent = user_agent

    async def load(self):
        self.user = UserDataStream(self,  f"{self.endpoint}/user", self.user_agent)
        self.market = MarketDataStream(self,  f"{self.endpoint}/market", self.user_agent)
        await self.user.connect()
        await self.market.connect()
       

    def _generate_signature(self, data):
        return hmac.new(
            self.api_secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha256,
        ).hexdigest()