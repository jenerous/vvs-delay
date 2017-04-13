#!/usr/bin/python

from cloudant import Cloudant
import atexit
import cf_deployment_tracker
import os
import json
import threading
from crawler import Crawler

# Emit Bluemix deployment event
cf_deployment_tracker.track()

data_base_name = 'vvs-delay-db'
client = None
data_base = None

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        data_base = client.create_database(data_base_name, throw_on_exists=False)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        data_base = client.create_database(data_base_name, throw_on_exists=False)

def main():
    global runner

    # # get a crawler instance
    crawler = Crawler()

    # import the api to use
    from crawler.crawlerhelpers import efa_beta

    # register api
    crawler.add_api( efa_beta.get_name(), efa_beta.get_base_url(), get_params_function=efa_beta.get_params, function_to_call=efa_beta.function_to_call, db=data_base)

    # run apis with the following station ids
    station_ids = ['6008']
    runner = threading.Thread(target=crawler.run, args=(station_ids))
    runner.start()
    crawler.log('Crawler is running', log=True)



@atexit.register
def shutdown():
    if runner:
        runner.join()
    if client:
        client.disconnect()

if __name__ == '__main__':
    main()
