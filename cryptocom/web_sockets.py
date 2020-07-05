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
        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = f"crypto.com (https://git.io/crypto.com, {__version__})"

    async def connect(self):
        async with aiohttp.ClientSession() as session:
            self.web_socket = await session.ws_connect(self.endpoint)
            self.request_id = 0
            while await self._handle_connection(self.web_socket):
                pass

    async def _handle_connection(self, web_socket):
        msg = await web_socket.receive()
        if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSE):
            logging.error("The websocket is closed! Trying to reconnect.")
            await self.connect() #todo: avoid reaching recursion limit

        elif msg.type is aiohttp.WSMsgType.ERROR:
            logging.error(f"Something went wrong with the websocket, reconnecting...")
            await self.connect() #todo: avoid reaching recursion limit

        data = json.loads(msg.data)
        if "code" in data:
            code = data["code"]
            self._handle_errors(code, data)

        if "method" in data:
            method = data["method"]
            asyncio.create_task(self._handle_response(method, data))

        return True

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
        #await self.web_socket.send_json(request)

    async def _handle_response(self, method, data):
        if method == "public/heartbeat":
            logging.debug("HEARTBEAT")
            await self._heartbeat(data["id"])
        else:
            logging.debug("TEST:" + data)

    def _handle_errors(self, code, data):
        pass

    async def _heartbeat(self, request_id):
        await self.request("public/respond-heartbeat", request_id=request_id)

    async def auth(self):
        await self.request("public/auth", signed=True)
