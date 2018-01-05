import time
import requests
import re
import sys
from termcolor import colored, cprint
from pprint import pprint
import ujson
from datetime import datetime
import humanize
import pyperclip
import winsound
import json
import tools

requests.models.json = ujson

# PCJ
def search_market_value(items_market_db, item_name, item_frame_type, item_type_line, socket_link_amount):
    for item in items_market_db:

        # PCJ

        if item['name'] == item_name and item['itemClass'] == item_frame_type and item['baseType'] == item_type_line:
            if socket_link_amount == 5 and item['links'] == socket_link_amount:
                return float(item['chaosValue'])

            if socket_link_amount == 6 and item['links'] == socket_link_amount:
                return float(item['chaosValue'])

            if socket_link_amount < 5 and item['links'] < 5:
                return float(item['chaosValue'])

    return 0.0


# stahes is from "http://www.pathofexile.com/api/public-stash-tabs?id="
# market_db is from por ninja
def find_items(market_db, stashes):
    # scan stashes available...

    for stash in stashes:
        character_name = stash.get('lastCharacterName')
        stash_name = stash.get('stash')
        items = stash.get('items')

        # log("{}, {}, {} items".format(character_name, stash_name, len(items)))

        # todo: compare number of unique items found (frameType) with number of priced items
        # log("amount of items {}".format(len(items)))
        for item in items:
            # discard any non-league stash
            if item.get('league') != u'Hardcore Abyss':
                continue

            # define some variables used to compare with poe.ninja
            item_name = re.sub(r'<<.*>>', '', item.get('name'))
            item_type_line = re.sub(r'<<.*>>', '', item.get('typeLine'))
            item_price = item.get('note', '')
            item_frame_type = item.get('frameType')

            # PCJ
            item_sockets = item.get('sockets')

            # define official name and price
            if item_name == '': item_name = item_type_line
            if item_price == '': item_price = stash_name

            # check if it is priced (chaos only)
            if (item_price.startswith("~b/o") or item_price.startswith("~price")) and item_price.endswith("chaos"):
                # todo: make this beautiful
                item_price = item_price.replace("~b/o ", "")
                item_price = item_price.replace("~price ", "")
                item_price = item_price.replace(" chaos", "")
                corrupted = item.get('corrupted', None)

                try:
                    item_price = float(item_price)
                except:
                    continue

                # Essence = frameType: 5
                if 'Atziri\'s Splendour' in item_name or 'Doryani\'s Invitation' in item_name or 'Kaom\'s Root' in item_name or 'Piscator\'s Vigil' in item_name or 'Voll\'s Vision' in item_name or 'Vessel of Vinktar' in item_name or 'Divinarius' in item_name or 'Kintsugi' in item_name or 'Allelopathy' in item_name or 'Cherrubim\'s Maleficence' in item_name or 'Realm Ender' in item_name or 'Karui Charge' in item_name or 'Edge of Madness' in item_name or 'Ngamahu Tiki' in item_name or 'Abyssus' in item_name or 'First Piece of Directions' in item_name or 'Vessel of Vinktar' in item_name or 'Second Piece of Directions' in item_name or 'Fourth Piece of Focus' in item_name or 'The Fracturing Spinner' in item_name or 'Izaro\'s Turmoil' in item_name:
                    continue

                # PCJ - 9/6/2017
                socket_link_amount = 0
                if hasattr(item_sockets, 'item_socket'): # PCJ - 1/5/2018
                    for item_socket in item_sockets:
                        if(item_socket['group'] == 0):
                            socket_link_amount = socket_link_amount+1

                item_market_value = search_market_value(market_db, item_name, item_frame_type, item_type_line, socket_link_amount)

                if item_market_value != 0.0 and item_price != 0.0 and item_market_value >= 5.0:
                    # evaluate price versus market
                    perc_decrease = ((item_market_value - item_price) / item_market_value) * 100

                    #log("{}, price: {} market value: {}".format(item_name, item_price, item_market_value))

                    if perc_decrease >= 50:
                        priceInt = int(item_price)
                        poe = "@{} Hi, I would like to buy your {} listed for {} chaos in Hardcore Abyss (stash tab \"{}\"; position: left {}, top {})".format(character_name, item_name, priceInt, stash_name, item.get('x'), item.get('y'))
                        pyperclip.copy(poe)
                        log("->>> @{} Hi, I would like to buy your {} listed for {} chaos in Hardcore Abyss (stash tab \"{}\"; position: left {}, top {}) , market_value: {} -{}%, corrupted: {}".format(character_name, item_name, priceInt, stash_name, item.get('x'), item.get('y'), item_market_value, round(perc_decrease), corrupted))
                        winsound.PlaySound('sound.wav', winsound.SND_FILENAME)
                        #pprint(item)
                    elif perc_decrease >= 30:
                        priceInt = int(item_price)
                        poe = "@{} Hi, I would like to buy your {} listed for {} chaos in Hardcore Abyss (stash tab \"{}\"; position: left {}, top {})".format(character_name, item_name, priceInt, stash_name, item.get('x'), item.get('y'))
                        pyperclip.copy(poe)
                        log("->>> @{} Hi, I would like to buy your {} listed for {} chaos in Hardcore Abyss (stash tab \"{}\"; position: left {}, top {}) , market_value: {} -{}%, corrupted: {}".format(character_name, item_name, priceInt, stash_name, item.get('x'), item.get('y'), item_market_value, round(perc_decrease), corrupted))
                        winsound.PlaySound('sound.wav', winsound.SND_FILENAME)
                    elif perc_decrease >= 20:
                    	priceInt = int(item_price)
                    	poe = "@{} Hi, I would like to buy your {} listed for {} chaos in Hardcore Abyss (stash tab \"{}\"; position: left {}, top {})".format(character_name, item_name, priceInt, stash_name, item.get('x'), item.get('y'))
                    	pyperclip.copy(poe)
                    	log("->>> @{} Hi, I would like to buy your {} listed for {} chaos in Hardcore Abyss (stash tab \"{}\"; position: left {}, top {}) , market_value: {} -{}%, corrupted: {}".format(character_name, item_name, priceInt, stash_name, item.get('x'), item.get('y'), item_market_value, round(perc_decrease), corrupted))
                    	winsound.PlaySound('sound.wav', winsound.SND_FILENAME)


def log(txt):
    print("[{}] {}".format(str(datetime.now().strftime('%H:%M:%S.%f')),txt))

def main():

    with open('./config.json') as data_file:
        droneData = json.load(data_file)

    log("Starting...")

    ### MARKET VALUE
    market_value_routine = droneData.get("marketValueRoutine")
    method_to_call = getattr(tools, market_value_routine.get("getMarketValueFunction"))
    method_attributes = market_value_routine.get("marketValueUrls")
    items_market_db = method_to_call(method_attributes)
    ### MARKET VALUE END

    ### STATS
    stats_routine = droneData.get("statsRoutine")
    stats_method = getattr(tools, stats_routine.get("getStatsFunction"))
    url_api = stats_routine.get('url_api')
    next_change_id = stats_method(stats_routine)
    ### STATS END

    log("Ready to go.")
    while True:
        start_time = time.time()

        params = {'id': next_change_id}
        request_result = requests.get(url_api, params = params)

        ## parsing structure
        data = request_result.json()

        ## setting next change id
        next_change_id = data['next_change_id']

        ## attempt to find items...
        find_items(items_market_db, data['stashes'])

        # log("Fetching next change id: {} - {}".format(next_change_id, humanize.naturalsize(len(r.content))))
        total_time = time.time() - start_time

        if total_time < 1:
            time.sleep(1 - total_time)

if __name__ == "__main__":
    main()
