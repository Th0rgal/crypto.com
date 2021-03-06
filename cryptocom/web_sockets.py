from . import __version__
import aiohttp
import asyncio
import logging
import time
import json


class DataStream:
    def __init__(self, client, endpoint, user_agent):
        self.client = client
        self.endpoint = endpoint
        self.enabled = False
        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = f"crypto.com (https://git.io/crypto.com, {__version__})"

    async def connect(self):
        self.request_id = 0
        asyncio.create_task(self.start_session())
        while not self.enabled:
            await asyncio.sleep(1)

    async def start_session(self):
        async with aiohttp.ClientSession() as session:
            self.web_socket = await session.ws_connect(self.endpoint)
            self.enabled = True
            await self._handle_connection()

    async def _handle_connection(self):
        while True:
            print("looped!")
            msg = await self.web_socket.receive()
            print("test")
            if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSE):
                logging.error("The websocket is closed! Trying to reconnect.")
                await self.connect()  # todo: avoid reaching recursion limit

            elif msg.type is aiohttp.WSMsgType.ERROR:
                logging.error(
                    f"Something went wrong with the websocket, reconnecting..."
                )
                await self.connect()  # todo: avoid reaching recursion limit

            data = json.loads(msg.data)
            if "code" in data:
                code = data["code"]
                self._handle_errors(code, data)

            if "method" in data:
                method = data["method"]
                asyncio.create_task(self._handle_response(method, data))

    async def request(
        self, method, params=None, request_id=None, response=False, signed=False
    ):
        if not request_id:
            request_id = self.request_id
            self.request_id += 1
        request = {
            "id": request_id,
            "method": method,
            "nonce": time.time(),
        }
        if params:
            request["params"] = params
        if signed:
            param_string = ""
            if "params" in request:
                for key in request["params"]:
                    param_string += key
                    param_string += str(request["params"][key])

            payload = (
                request["method"]
                + str(request["id"])
                + self.client.api_key
                + param_string
                + str(request["nonce"])
            )
            request.update(
                {
                    "api_key": self.client.api_key,
                    "sig": self.client._generate_signature(payload),
                }
            )
        await self.web_socket.send_json(request)

    async def _handle_response(self, method, data):
        print("ABC:", data)
        if method == "public/heartbeat":
            await self._heartbeat(data["id"])
        else:
            print("TEST:" + data)

    def _handle_errors(self, code, data):
        pass

    async def _heartbeat(self, request_id):
        await self.request("public/respond-heartbeat")

    async def auth(self):
        await self.request("public/auth", signed=True)


class UserDataStream(DataStream):
    def __init__(self, client, endpoint, user_agent):
        super().__init__(client, endpoint, user_agent)


class MarketDataStream(DataStream):
    def __init__(self, client, endpoint, user_agent):
        super().__init__(client, endpoint, user_agent)

    async def get_instruments(self):
        await self.request("public/get-instruments")
