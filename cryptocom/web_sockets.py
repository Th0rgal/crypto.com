from . import __version__
import aiohttp
import asyncio
import logging
import json


class DataStream:
    def __init__(self, client, endpoint, user_agent):
        self.client = client
        self.endpoint = endpoint
        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = f"crypto.com (https://git.io/crypto.com, {__version__})"

    async def connect(self):
        session = aiohttp.ClientSession()
        self.web_socket = await session.ws_connect(self.endpoint)

        while True:
            msg = await self.web_socket.receive()
            if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSE):
                logging.error(
                    "Trying to receive something while the websocket is closed! Trying to reconnect."
                )
                return await self.connect()

            elif msg.type is aiohttp.WSMsgType.ERROR:
                logging.error(
                    f"Something went wrong with the websocket, reconnecting..."
                )
                return await self.connect()

            data = json.loads(msg.data)
            if "code" in data:
                code = data["code"]
                self._handle_errors(code, data)

            if "method" in data:
                method = data["method"]
                asyncio.create_task(self._handle_response(method, data))

    async def _handle_response(self, method, data):
        if method == "public/heartbeat":
            await self._heartbeat(data["id"])

    def _handle_errors(self, code, data):
        pass

    async def _heartbeat(self, id):
        await self.web_socket.send_json(
            {"id": id, "method": "public/respond-heartbeat"}
        )
