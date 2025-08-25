import sys
import json
import logging
import warnings
import requests
import datetime

from typing import Union

warnings.filterwarnings("ignore")

BREAKER: str = "\n" + 50 * "*" + "\n"
TIMES_NAMES: tuple = ("Fajr", "Dhuhr", "Asr", "Maghrib", "Isha")
HEADERS: dict = {"Content-Type": "application/json"}

LOGGER = logging.getLogger("main.py")
logging.basicConfig(filename="run.log", encoding='utf-8', level=logging.DEBUG)


def get_prayer_times(lat: str, long: str) -> dict:
    today = datetime.datetime.now().date().strftime("%d-%m-%Y")

    url = f"https://api.aladhan.com/v1/timings/{today}?latitude={lat}&longitude={long}&method=4"

    response = requests.get(url)
    if response.status_code != 200:
        return response.status_code, response.text

    LOGGER.info("----- SUCCESS -----")
    LOGGER.info(datetime.datetime.now().strftime("%d-%m-%Y - %H:%M:%S - Retrieved Timings"))
    LOGGER.info(f"Latitude={lat}, Longitude={long}")

    return {
        k: response.json()["data"]["timings"][k]
        for k in TIMES_NAMES
        if k in response.json()["data"]["timings"]
    }


def save_prayer_times(lat: str, long: str):
    # today = datetime.datetime.now().date().strftime("%d-%m-%Y")

    # url = f"https://api.aladhan.com/v1/timings/{today}?latitude={lat}&longitude={long}&method=4"

    # response = requests.get(url)
    # if response.status_code != 200:
    #     return response.status_code, response.text

    # timings = {
    #     k: response.json()["data"]["timings"][k]
    #     for k in TIMES_NAMES
    #     if k in response.json()["data"]["timings"]
    # }

    timings = get_prayer_times(lat, long)

    json.dump(timings, open("temp.json", "w"))

    LOGGER.info("----- SUCCESS -----")
    LOGGER.info(datetime.datetime.now().strftime("%d-%m-%Y - %H:%M:%S - Saved Timings"))
    LOGGER.info(f"Latitude={lat}, Longitude={long}")
    

def check(server_ip: str):
    now = datetime.datetime.now()
    current_time = now.replace(second=0, microsecond=0)

    timings = json.load(open("temp.json", "r"))
    timings = [t for t in timings.values()]
    timings = [datetime.datetime.strptime(t, "%H:%M").time() for t in timings]

    LOGGER.info("----- CHECK -----")
    LOGGER.info(datetime.datetime.now().strftime("Now - %H:%M"))

    for timing in timings:
        timing = datetime.datetime.combine(now.date(), timing)

        # Activate the trigger 5 minutes before the prayer time
        trigger_dt = timing - datetime.timedelta(minutes=5)

        if trigger_dt == current_time:
            url = f"https://{server_ip}/triplecare/eventHttpRequest.php?id=12&key=513e02950d9d0f4838eede664aa86df3&status=1"
            try:
                response = requests.get(url, verify=False, timeout=1)
                if response.status_code == 200:
                    LOGGER.info("----- SUCCESS -----")
                    LOGGER.info(datetime.datetime.now().strftime("%d-%m-%Y - %H:%M:%S - Event Activated"))
            except Exception as e:
                LOGGER.debug("----- FAILURE -----")
                LOGGER.debug(e)
                break
        

def main():
    args_1: tuple = ("--operation", "-op")
    args_2: tuple = ("--server-ip", "-sip")

    operation: Union[str, None] = None
    server_ip: str = "10.10.0.201"

    if args_1[0] in sys.argv:
        operation = sys.argv[sys.argv.index(args_1[0]) + 1]
    if args_1[1] in sys.argv:
        operation = sys.argv[sys.argv.index(args_1[1]) + 1]
    
    if args_2[0] in sys.argv:
        server_ip = sys.argv[sys.argv.index(args_2[0]) + 1]
    if args_2[1] in sys.argv:
        server_ip = sys.argv[sys.argv.index(args_2[1]) + 1]

    if operation is None:
        LOGGER.info(datetime.datetime.now().strftime("%d-%m-%Y - %H:%M:%S - No Operation Specified"))
        sys.exit(f"{BREAKER}\nNo Operation Specified\n{BREAKER}")

    if operation == "save":
        save_prayer_times(lat="24.7136", long="46.6753")
    
    if operation == "get":
        _ = get_prayer_times(lat="24.7136", long="46.6753")

    if operation == "check":
        check(server_ip)


if __name__ == "__main__":
    sys.exit(main() or 0)
