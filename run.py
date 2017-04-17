#!/usr/bin/python

from cloudant import Cloudant
import atexit
import cf_deployment_tracker
import os
import threading
from crawler import Crawler

# Emit Bluemix deployment event
cf_deployment_tracker.track()

crawler = None
runner  = None

def main():
    global crawler, runner

    # get a crawler instance
    crawler = Crawler()

    # import the apis to use
    from crawler.crawlerhelpers.efa_beta import API_efaBeta
    api_efa_beta = API_efaBeta()

    # register api
    crawler.add_api( api_efa_beta.name, api_efa_beta.baseurl, get_params_function=api_efa_beta.get_params, function_to_call=api_efa_beta.function_to_call)

    #import the db to use
    from crawler.crawlerhelpers import cloudant_db

    crawler.set_db_session(cloudant_db.get_db_session('vcap-local.json'), 'vvs-delay-db')

    # run apis with the following station ids
    station_ids = ['6008']
    runner = threading.Thread(target=crawler.run, args=(station_ids, ))
    runner.start()
    crawler.log('Crawler is running', log=True)


@atexit.register
def shutdown():
    global crawler, runner

    if runner:
        runner.join()
    crawler.close_db_session()

if __name__ == '__main__':
    main()
