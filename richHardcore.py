import json
import re
import sys
import time
import winsound
from datetime import datetime
from pprint import pprint

import requests

import humanize
import pyperclip
import tools
from termcolor import colored, cprint

# stashes is from "http://www.pathofexile.com/api/public-stash-tabs?id="
# market_db is from por ninja

def safe_json(request_result):
    try:
        json_object = request_result.json()
    except ValueError as e:
        log("ValueError when getting json")
        log(e)
        return False
    else:
        return json_object


def log(txt):
    print("[{}] {}".format(str(datetime.now().strftime('%H:%M:%S.%f')),txt))

def main():

    with open('./config.json') as data_file:
        droneData = json.load(data_file)

    log("Starting...")

    ### MARKET VALUE
    market_value_routine = droneData.get("marketValueRoutine")
    market_function = getattr(tools, market_value_routine.get("getMarketValueFunction"))
    method_attributes = market_value_routine.get("marketValueUrls")
    items_market_db = market_function(method_attributes)
    ### MARKET VALUE END

    ### STATS
    stats_routine = droneData.get("statsRoutine")
    stats_function = getattr(tools, stats_routine.get("getStatsFunction"))
    url_api = stats_routine.get('url_api')
    next_change_id = stats_function(stats_routine)
    ### STATS END

    find_items_routine = droneData.get("findItemsRoutine")
    find_items_function = getattr(tools, find_items_routine.get("findItemsRoutineFunction"))

    log("Ready to go.")
    while True:
        start_time = time.time()

        params = {'id': next_change_id}
        request_result = requests.get(url_api, params = params)

        ## parsing structure
        ##data = request_result.json()
        data = safe_json(request_result)
        if not data:
            continue

        ## setting next change id
        next_change_id = data['next_change_id']

        ## attempt to find items...
        find_items_function(items_market_db, data['stashes'], find_items_routine)

        # log("Fetching next change id: {} - {}".format(next_change_id, humanize.naturalsize(len(r.content))))
        total_time = time.time() - start_time

        if total_time < 1:
            time.sleep(1 - total_time)

if __name__ == "__main__":
    main()
