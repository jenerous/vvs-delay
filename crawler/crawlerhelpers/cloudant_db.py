from cloudant import Cloudant
import json
import os
from crawler.logging import logfunctions
from time import sleep


def get_client_session(cred_file):
    creds = None

    if 'VCAP_SERVICES' in os.environ:
        vcap = json.loads(os.getenv('VCAP_SERVICES'))
        if 'cloudantNoSQLDB' in vcap:
            creds = vcap['cloudantNoSQLDB'][0]['credentials']
            logfunctions.log("Found credentials in ENV")
    elif os.path.isfile(cred_file):
        with open(cred_file) as f:
            vcap = json.load(f)
            creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
            logfunctions.log("Found local credentials")
    else:
        logfunctions.error("Could not find credentials")

    url = 'https://' + creds['host']
    user = creds['username']
    password = creds['password']
    return Cloudant(user, password, url=url, connect=True)


class CloudantDB(object):

    def __init__(self, cred_file, db_name):
        self.name = db_name
        self.client = get_client_session(cred_file)
        self.db = self.client.create_database(db_name, throw_on_exists=False)
        self.max_req_per_sec = 10
        logfunctions.log("Connected to database '{}'".format(db_name))

    def close_session(self):
        if self.client:
            self.client.disconnect()
            logfunctions.log("Disconnected from database '{}'".format(self.name))

    def write_to_db(self, results):
        logfunctions.log("Writing to database '{}'".format(self.name))
        if isinstance(results, list):
            if len(results) >= self.max_req_per_sec:
                for r in range(self.max_req_per_sec, len(results), self.max_req_per_sec):
                    for idx in range(r - self.max_req_per_sec, r):
                        self.db.create_document(results[r])
                    logfunctions.log('delaying requests, because maximum requests per second '
                                     'limit could be reached')
                    sleep(1.5)
            else:
                for r in range(len(results)):
                    self.db.create_document(results[r])
        else:
            self.db.create_document(results)
