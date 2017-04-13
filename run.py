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

def main():

    # get a crawler instance
    crawler = Crawler()

    # import the api to use
    from crawler.crawlerhelpers import efa_beta

    #import the db to use
    from crawler.crawlerhelpers import cloudant_db

    # register api
    crawler.add_api( efa_beta.get_name(), efa_beta.get_base_url(), get_params_function=efa_beta.get_params, function_to_call=efa_beta.function_to_call)

    crawler.set_db_session(cloudant_db.get_db_session('vcap-local.json'), 'vvs-delay-db')

    # run apis with the following station ids
    station_ids = ['6008']
    runner = threading.Thread(target=crawler.run, args=(station_ids))
    runner.start()
    crawler.log('Crawler is running', log=True)


@atexit.register
def shutdown():
    if runner:
        runner.join()
    crawler.close_db_session()

if __name__ == '__main__':
    main()
