import os
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
LOCATION_INFO = {
    "riyadh" : ["24.1736", "46.6753", "id=12&key=513e02950d9d0f4838eede664aa86df3"],
    "jeddah" : ["21.5292", "39.1611"],
}
HEADERS: dict = {"Content-Type": "application/json"}

SAVE_DIR: str = os.path.join(os.getcwd(), "data")
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

LOGGER = logging.getLogger("main.py")
logging.basicConfig(filename=os.path.join(SAVE_DIR, "run.log"), encoding='utf-8', level=logging.DEBUG)


def get_prayer_times(location: str) -> dict:
    today = datetime.datetime.now().date().strftime("%d-%m-%Y")
    lat = LOCATION_INFO[location][0]
    long = LOCATION_INFO[location][1]

    url = f"https://api.aladhan.com/v1/timings/{today}?latitude={lat}&longitude={long}&method=4"

    response = requests.get(url)
    if response.status_code != 200:
        return response.status_code, response.text

    LOGGER.info("----- SUCCESS -----")
    LOGGER.info(datetime.datetime.now().strftime("%d-%m-%Y - %H:%M:%S - Retrieved Timings"))
    LOGGER.info(f"Location: {location}")

    return {
        k: response.json()["data"]["timings"][k]
        for k in TIMES_NAMES
        if k in response.json()["data"]["timings"]
    }


def save_prayer_times(location: str) -> None:
    timings = get_prayer_times(location)

    json.dump(timings, open(os.path.join(SAVE_DIR, f"{location}.json"), "w"))

    LOGGER.info("----- SUCCESS -----")
    LOGGER.info(datetime.datetime.now().strftime("%d-%m-%Y - %H:%M:%S - Saved Timings"))
    LOGGER.info(f"Location: {location}")

    
def check(server_ip: str, location: str):
    now = datetime.datetime.now()
    current_time = now.replace(second=0, microsecond=0)

    timings = json.load(open(os.path.join(SAVE_DIR, f"{location}.json"), "r"))
    timings = [t for t in timings.values()]
    timings = [datetime.datetime.strptime(t, "%H:%M").time() for t in timings]

    LOGGER.info("----- CHECK -----")
    LOGGER.info(datetime.datetime.now().strftime("Now - %H:%M"))

    for timing in timings:
        timing = datetime.datetime.combine(now.date(), timing)

        if timing < now:
            continue

        # Activate the trigger 5 minutes before the prayer time
        trigger_dt = timing - datetime.timedelta(minutes=5)

        if trigger_dt == current_time:
            activate(server_ip, location)


def activate(server_ip, location: str):
    url = f"https://{server_ip}/triplecare/eventHttpRequest.php?{LOCATION_INFO[location][2]}&status=1"
    try:
        response = requests.get(url, verify=False, timeout=1)
        if response.status_code == 200:
            LOGGER.info("----- SUCCESS -----")
            LOGGER.info(datetime.datetime.now().strftime("%d-%m-%Y - %H:%M:%S - Event Activated"))
    except Exception as e:
        LOGGER.debug("----- FAILURE -----")
        LOGGER.debug(e)
        

def main():
    args_1: tuple = ("--operation", "-op")
    args_2: tuple = ("--server-ip", "-sip")
    args_3: tuple = ("--location", "-loc")
    args_4: tuple = "--event-debug"

    operation: Union[str, None] = None
    server_ip: str = "10.10.0.201"
    location: str = "riyadh"
    event_debug: bool = False

    if args_1[0] in sys.argv:
        operation = sys.argv[sys.argv.index(args_1[0]) + 1]
    if args_1[1] in sys.argv:
        operation = sys.argv[sys.argv.index(args_1[1]) + 1]
    
    if args_2[0] in sys.argv:
        server_ip = sys.argv[sys.argv.index(args_2[0]) + 1]
    if args_2[1] in sys.argv:
        server_ip = sys.argv[sys.argv.index(args_2[1]) + 1]
    
    if args_3[0] in sys.argv:
        location = sys.argv[sys.argv.index(args_3[0]) + 1]
    if args_3[1] in sys.argv:
        location = sys.argv[sys.argv.index(args_3[1]) + 1]
    
    if args_4 in sys.argv: 
        event_debug = True

    if not event_debug:
        if operation is None:
            LOGGER.info(datetime.datetime.now().strftime("%d-%m-%Y - %H:%M:%S - No Operation Specified"))
            sys.exit(f"{BREAKER}\nNo Operation Specified\n{BREAKER}")
        
        if operation == "save":
            save_prayer_times(location)
        
        if operation == "get":
            print(get_prayer_times(location))

        if operation == "check":
            check(server_ip, location)

    else: 
        save_prayer_times(location)
        activate(server_ip, location)


if __name__ == "__main__":
    sys.exit(main() or 0)
