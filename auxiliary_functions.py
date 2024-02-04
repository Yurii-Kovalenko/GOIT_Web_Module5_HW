from sys import argv

from datetime import datetime

from datetime import timedelta

POSSIBLE_ADDITIONAL_CURRENCIES = ["CHF", "CZK", "GBP", "PLN"]

WORDS_OF_REQUEST_FOR_HELP = ["HELP", "-H", "--H", "/H"]

HINT = """
The program outputs currency rates for several days, the maximum is 10.
The base currencies are EUR and USD. Additional currencies are possible: CHF, CZK, GBP, PLN.
In the arguments, enter the number of days and additional currencies separated by a space.
"""


def list_days(number_of_days: int) -> list[str]:
    result = []
    date_now = datetime.now()
    for amount_days in range(number_of_days):
        new_date = (date_now - timedelta(days=amount_days)).strftime("%d.%m.%Y")
        result.append(new_date)
    return result


def enter_number() -> int:
    while True:
        number_in_str = input("Enter the number of days: ")
        if number_in_str.isdigit():
            result = int(number_in_str)
            if result == 0:
                result = 1
            break
        else:
            print("You only need to enter numbers.")
    return result


def need_help() -> bool:
    result = False
    if len(argv) > 1:
        for i in range(1, len(argv)):
            if argv[i].upper() in WORDS_OF_REQUEST_FOR_HELP:
                result = True
                print(HINT)
                break
    return result


def finding_the_number_of_days(arguments: list) -> int:
    number_of_days = 0
    for i in range(1, len(arguments)):
        if arguments[i].isdigit():
            number_of_days = int(arguments[i])
            break
    return number_of_days


def finding_additional_currencies(arguments: list) -> list[str]:
    result = []
    for i in range(1, len(arguments)):
        if arguments[i].upper() in POSSIBLE_ADDITIONAL_CURRENCIES:
            result.append(arguments[i].upper())
    return result


def process_arguments() -> tuple[int, list[str]]:
    number_of_days = 0
    list_of_additional_currencies = []
    if not need_help():
        if len(argv) > 1:
            number_of_days = finding_the_number_of_days(argv)
            list_of_additional_currencies = finding_additional_currencies(argv)
        if number_of_days == 0:
            number_of_days = enter_number()
        if number_of_days > 10:
            number_of_days = 10
            print("Viewing courses is possible no more than for the last 10 days.")
    return number_of_days, list_of_additional_currencies


def adapter(privatbank_jsons: list[dict], list_of_currencies) -> list[dict]:
    result = []
    for privatbank_json in privatbank_jsons:
        privatbank_exchange_rate = privatbank_json["exchangeRate"]
        exchange_rates = {}
        for currency in list_of_currencies:
            for privatbank_info_for_one_currency in privatbank_exchange_rate:
                if currency == privatbank_info_for_one_currency["currency"]:
                    exchange_rates[currency] = {
                        "sale": privatbank_info_for_one_currency["saleRate"],
                        "purchase": privatbank_info_for_one_currency["purchaseRate"],
                    }
                    break
        exchange_rates_for_day = {}
        exchange_rates_for_day[privatbank_json["date"]] = exchange_rates
        result.append(exchange_rates_for_day)
    return result


def view_in_table(my_json: list[dict]) -> str:
    dict_of_currencies = list(my_json[0].values())[0]
    number_of_currencies = len(dict_of_currencies)
    empty_line = "-" * (14 + 22 * number_of_currencies) + "\n"
    empty_line_with_date = "|    Date    |" + "-" * (22 * number_of_currencies) + "\n"
    result = empty_line
    pattern_for_title = "|{:^12}|" + "{:^21}|" * number_of_currencies + "\n"
    result += pattern_for_title.format(
        "", *([currency for currency in dict_of_currencies])
    )
    result += empty_line_with_date
    pattern = "|{:^12}|" + "{:^10}|{:^10}|" * number_of_currencies + "\n"
    result += pattern.format("", *(["sale", "purchase"] * number_of_currencies))
    result += empty_line
    for dict_for_one_day in my_json:
        date_of_courses = list((dict_for_one_day.keys()))[0]
        dict_of_currencies = dict_for_one_day[date_of_courses]
        list_of_courses = []
        for currency in dict_of_currencies:
            list_of_courses.append(dict_of_currencies[currency]["sale"])
            list_of_courses.append(dict_of_currencies[currency]["purchase"])
        result += pattern.format(date_of_courses, *list_of_courses)
        result += empty_line
    return result
