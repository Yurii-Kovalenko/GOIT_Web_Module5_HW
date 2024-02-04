from platform import system as platform_system

import asyncio

from aiohttp import ClientSession

from aiohttp import ClientConnectorError

from auxiliary_functions import list_days

from auxiliary_functions import process_arguments

from auxiliary_functions import adapter

from auxiliary_functions import view_in_table


HPTTP_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

list_of_currencies = ["EUR", "USD"]

VIEW_ONLY_IN_TABLE = False


async def fetch_url(session: ClientSession, url: str) -> dict:
    try:
        async with session.get(f"{url}") as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error status: {response.status} for {url}")
    except ClientConnectorError as text_error:
        print(f"Connection error: {url}. ", str(text_error))


async def get_jsons(number_of_days: int) -> list[dict]:
    async with ClientSession() as session:
        result = await asyncio.gather(
            *(
                [
                    fetch_url(session, f"{HPTTP_URL}{day}")
                    for day in list_days(number_of_days)
                ]
            )
        )
    return result


def to_avoid_error():
    if platform_system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def view_jsons(privatbank_jsons: list[dict]) -> None:
    my_json = adapter(privatbank_jsons, list_of_currencies)
    if not VIEW_ONLY_IN_TABLE:
        print(my_json)
        print()
    print(view_in_table(my_json))


def main():
    number_of_days, list_of_additional_currencies = process_arguments()
    if number_of_days:
        list_of_currencies.extend(list_of_additional_currencies)
        to_avoid_error()
        privatbank_jsons = asyncio.run(get_jsons(number_of_days))
        view_jsons(privatbank_jsons)


if __name__ == "__main__":
    main()
