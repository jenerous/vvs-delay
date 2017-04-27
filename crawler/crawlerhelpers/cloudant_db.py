from cloudant import Cloudant
import json
import os
from crawler.logging import logfunctions

class CloudantDB(object):

    def __init__(self, cred_file, db_name):
        self.name = db_name
        creds = None

        if 'VCAP_SERVICES' in os.environ:
            vcap = json.loads(os.getenv('VCAP_SERVICES'))
            if 'cloudantNoSQLDB' in vcap:
                creds = vcap['cloudantNoSQLDB'][0]['credentials']

        elif os.path.isfile(cred_file):
            with open(cred_file) as f:
                vcap = json.load(f)
                creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']

        url = 'https://' + creds['host']
        user = creds['username']
        password = creds['password']
        self.client = Cloudant(user, password, url=url, connect=True)
        self.db = self.client.create_database(db_name, throw_on_exists=False)
        logfunctions.log("Connected to database " + db_name)

    def close_session(self):
        if self.db:
            self.db.disconnect()
            logfunctions.log("Disconnected from database " + self.name)

    def write_to_db(self, results):
        for r in results:
            self.db.create_document(r)