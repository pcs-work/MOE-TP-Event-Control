import sys
import json
import warnings
import requests
import datetime

from typing import Union

warnings.filterwarnings("ignore")

BREAKER: str = "\n" + 50 * "*" + "\n"
TIMES_NAMES: tuple = ("Fajr", "Dhuhr", "Asr", "Maghrib", "Isha")
HEADERS = {"Content-Type": "application/json"}


def get_prayer_times(lat: str, long: str) -> dict:
    today = datetime.datetime.now().date().strftime("%d-%m-%Y")

    url = f"https://api.aladhan.com/v1/timings/{today}?latitude={lat}&longitude={long}&method=4"

    response = requests.get(url)
    if response.status_code != 200:
        return response.status_code, response.text

    return {
        k: response.json()["data"]["timings"][k]
        for k in TIMES_NAMES
        if k in response.json()["data"]["timings"]
    }


def save_prayer_times(lat: str, long: str):
    today = datetime.datetime.now().date().strftime("%d-%m-%Y")

    url = f"https://api.aladhan.com/v1/timings/{today}?latitude={lat}&longitude={long}&method=4"

    response = requests.get(url)
    if response.status_code != 200:
        return response.status_code, response.text

    timings = {
        k: response.json()["data"]["timings"][k]
        for k in TIMES_NAMES
        if k in response.json()["data"]["timings"]
    }

    json.dump(timings, open("temp.json", "w"))


def prayer_event_handler(server_ip: str, activate: bool):
    if activate:
        url = f"https://{server_ip}/triplecare/eventHttpRequest.php?id=12&key=513e02950d9d0f4838eede664aa86df3&status=1"
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            return "Event Activated"


def check():
    hh = datetime.datetime.now().hour
    mm = datetime.datetime.now().min

    timings = json.load(open("temp.json", "r"))


def main():
    args: str = "--operation"

    operation: Union[str, None] = None

    if args in sys.argv:
        operation = sys.argv[sys.argv.index(args) + 1]

    if operation is None:
        sys.exit("No Operation")

    if operation == "save":
        save_prayer_times(lat="24.7136", long="46.6753")

    if operation == "get":
        _ = get_prayer_times(lat="24.7136", long="46.6753")

    if operation == "check":
        check()

if __name__ == "__main__":
    sys.exit(main() or 0)
