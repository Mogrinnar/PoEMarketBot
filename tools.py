from datetime import datetime
import requests
import humanize

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

