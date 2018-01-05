from datetime import datetime
import requests
import humanize
import re
import pyperclip
import winsound

def log(txt):
    print("[{}] {}".format(str(datetime.now().strftime('%H:%M:%S.%f')),txt))

def get_market_value(marketValueUrls):
    log("Pulling market price from poe.ninja...")
    items = []

    for url in marketValueUrls:
        log("Pulling {} ...".format(url))
        url = str(url)
        r = requests.get(url)

        lines = r.json().get('lines')
        if lines != None:
            for item in lines:
                items.append(item)

    log("Pulled prices from {} items price for poe.ninja".format(len(items)))

    return items


def get_stats(statsData):
    url_api = statsData.get('url_api')
    stats_url = statsData.get('url_stats')
    id_name = statsData.get('id_name')

    # get a starting point for next_change_id
    request_result = requests.get(stats_url)
    next_change_id = request_result.json().get(id_name)
    next_change_id = str(next_change_id)

    log("Skipping 10 next_change_id")

    for _ in range(10):
       params = {'id': next_change_id}
       request_result = requests.get(url_api, params=params)
       data = request_result.json()
       log("{} - {}".format(next_change_id, humanize.naturalsize(len(request_result.content))))
       if hasattr(data , str(id_name)):
           next_change_id = data[id_name]

    return next_change_id


def search_market_value(items_market_db, item_name, item_frame_type, item_type_line, socket_link_amount):
    for item in items_market_db:

        if item['name'] == item_name and item['itemClass'] == item_frame_type and item['baseType'] == item_type_line:
            if socket_link_amount == 5 and item['links'] == socket_link_amount:
                return float(item['chaosValue'])

            if socket_link_amount == 6 and item['links'] == socket_link_amount:
                return float(item['chaosValue'])

            if socket_link_amount < 5 and item['links'] < 5:
                return float(item['chaosValue'])

    return 0.0


def check_forbidden_names(names, item_name):
    for name in names:
        if name in item_name:
            return True

    return False


def find_items(market_db, stashes, routine_data):
    # scan stashes available...

    for stash in stashes:
        character_name = stash.get('lastCharacterName')
        stash_name = stash.get('stash')
        items = stash.get('items')

        critical_name = str(routine_data.get('itemCriticalCriteriaName'))
        critical_value = str(routine_data.get('itemCriticalCriteriaValue'))
        forbidden_names = routine_data.get('forbiddenNames')

        # log("{}, {}, {} items".format(character_name, stash_name, len(items)))

        # todo: compare number of unique items found (frameType) with number of priced items
        # log("amount of items {}".format(len(items)))
        for item in items:
            # discard any non-league stash
            if str(item.get(critical_name)) != critical_value:
                continue

            # define some variables used to compare with poe.ninja
            item_name = re.sub(r'<<.*>>', '', item.get('name'))
            item_type_line = re.sub(r'<<.*>>', '', item.get('typeLine'))
            item_price = item.get('note', '')
            item_frame_type = item.get('frameType')

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

                if check_forbidden_names(forbidden_names, item_name):
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
