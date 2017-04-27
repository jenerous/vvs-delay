#!/usr/bin/python

import atexit
import cf_deployment_tracker
import threading
from crawler import Crawler
import crawler.settings as settings
import importlib

# Emit Bluemix deployment event
cf_deployment_tracker.track()

crawler = None
runner  = None

def main():
    global crawler, runner

    # get a crawler instance
    crawler = Crawler()

    # import the apis to use
    for a in settings.APIS:
        api_module = importlib.import_module("crawler.crawlerhelpers." + a  )
        api = api_module.get_instance()
        # register api
        crawler.add_api( api.name, api.baseurl, get_params_function=api.get_params, function_to_call=api.function_to_call)

    #import the db to use
    from crawler.crawlerhelpers.cloudant_db import CloudantDB
    crawler.add_db(CloudantDB('vcap-local.json', settings.DB_NAME))

    # run apis with the following station ids
    runner = threading.Thread(target=crawler.run, args=(settings.STATION_IDS, ))
    runner.start()
    crawler.log('Crawler is running', log=True)


@atexit.register
def shutdown():
    global crawler, runner

    if runner:
        runner.join()
    crawler.shutdown()

if __name__ == '__main__':
    main()
