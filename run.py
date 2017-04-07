from cloudant import Cloudant
from flask import Flask, render_template, request, jsonify
import atexit
import cf_deployment_tracker
import os
import json
from crawler import Crawler

# Emit Bluemix deployment event
cf_deployment_tracker.track()

app = Flask(__name__)

client = None


def connect_to_db():
    if 'VCAP_SERVICES' in os.environ:
        vcap = json.loads(os.getenv('VCAP_SERVICES'))
        print('Found VCAP_SERVICES')
        if 'cloudantNoSQLDB' in vcap:
            creds = vcap['cloudantNoSQLDB'][0]['credentials']
            url = 'https://' + creds['host']

    elif os.path.isfile('vcap-local.json'):
        with open('vcap-local.json') as f:
            vcap = json.load(f)
            print('Found local VCAP_SERVICES')
            creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
            url = 'http://' + creds['host'] + ':' + creds['port']

    user = creds['username']
    password = creds['password']
    client = Cloudant(user, password, url=url, connect=True)

    return client

# On Bluemix, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8080
port = int(os.getenv('PORT', 8080))

@app.route('/')
def home():
    return render_template('index.html')

def main():
    app.run(host='0.0.0.0', port=port, debug=True)

    db_name = 'vvs-delay-db'
    client = connect_to_db()
    db = client.create_database(db_name, throw_on_exists=False)

    # get a crawler instance
    crawler = Crawler()

    # import the api to use
    from crawler.crawlerhelpers import efa_beta

    # register api
    crawler.add_api( efa_beta.get_name(), efa_beta.get_base_url(), get_params_function=efa_beta.get_params, function_to_call=efa_beta.function_to_call)
    # crawler.add_db(db)

    # run apis with the following station ids
    station_ids = ['6008']
    crawler.run(station_ids)

@atexit.register
def shutdown():
    if client:
        client.disconnect()

if __name__ == '__main__':
    main()
