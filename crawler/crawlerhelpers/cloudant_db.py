from cloudant import Cloudant
import json
import os

def get_db_session(cred_file):

    creds = None

    if 'VCAP_SERVICES' in os.environ:
        vcap = json.loads(os.getenv('VCAP_SERVICES'))
        print('Found VCAP_SERVICES')
        if 'cloudantNoSQLDB' in vcap:
            creds = vcap['cloudantNoSQLDB'][0]['credentials']
            url = 'https://' + creds['host']

    elif os.path.isfile(cred_file):
        with open(cred_file) as f:
            vcap = json.load(f)
            print('Found local VCAP_SERVICES')
            creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
            url = 'http://' + creds['host'] + ':' + creds['port']

    user = creds['username']
    password = creds['password']
    client = Cloudant(user, password, url=url, connect=True)

    return client
