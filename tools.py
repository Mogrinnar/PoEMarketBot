def get_market_value(marketValueUrls):
    log("Pulling market price from poe.ninja...")
    items = []

    for url in marketValueUrls:
        log("Pulling {} ...".format(url))
        r = requests.get(url)

        for item in r.json().get('lines'):
            items.append(item)

    log("Pulled prices from {} items price for poe.ninja".format(len(items)))

    return items
