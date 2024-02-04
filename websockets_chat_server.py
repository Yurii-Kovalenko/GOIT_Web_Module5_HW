import asyncio

import logging

import websockets

from websockets import WebSocketServerProtocol

from websockets.exceptions import ConnectionClosedOK

from auxiliary_functions import adapter

from auxiliary_functions import view_in_table

from main import get_jsons

from auxiliary_functions import finding_the_number_of_days

from auxiliary_functions import finding_additional_currencies

from aiopath import AsyncPath

from aiofile import async_open

from datetime import datetime


logging.basicConfig(level=logging.INFO)

list_hello = ["hello", "hello!", "hi!", "hi"]

list_bye = ["goodbye", "goodbye!", "exit", "quit", "bye"]

BASE_CURRENCIES = ("EUR", "USD")

LOG_FILE = "log.txt"


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        self.clients.add(ws)
        logging.info(f"{ws.remote_address} connects")

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f"{ws.remote_address} disconnects")

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def exchange_table(self, message: str) -> str:
        number_of_days = 1
        list_of_currencies = list(BASE_CURRENCIES)
        print(list_of_currencies)
        if len(message) > 8:
            list_of_message = message.split()
            number_of_days = finding_the_number_of_days(list_of_message)
            list_of_currencies.extend(finding_additional_currencies(list_of_message))
            print(list_of_currencies)
            if number_of_days == 0:
                number_of_days = 1
            if number_of_days > 10:
                number_of_days = 10
        privatbank_jsons = await get_jsons(number_of_days)
        my_json = adapter(privatbank_jsons, list_of_currencies)
        result = f"\n{view_in_table(my_json)}"
        return result

    async def write_log(self, message: str) -> None:
        apath = AsyncPath(LOG_FILE)
        if await apath.exists() and await apath.is_file():
            type_of_processing = "a"
        else:
            if await apath.exists() and await apath.is_dir():
                type_of_processing = ""
            else:
                type_of_processing = "w+"
        if type_of_processing:
            async with async_open(LOG_FILE, type_of_processing) as afw:
                await afw.write(f"{str(datetime.now())[:19]} - {message}\n")

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message[:8].lower() == "exchange":
                await self.write_log(message)
                table = await self.exchange_table(message)
                await ws.send(table)
            if message.lower() in list_hello:
                await ws.send("Hello!")
            if message.lower() in list_bye:
                await ws.send("Goodbye!")
            for client in self.clients:
                if client != ws:
                    await client.send(f"{ws.remote_address}: {message}")


async def main():
    server = Server()

    async with websockets.serve(server.ws_handler, "localhost", 8765) as server:
        await server.server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown")
