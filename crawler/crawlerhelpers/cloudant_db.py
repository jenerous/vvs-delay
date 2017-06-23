
import atexit
from cloudant import Cloudant
import json
import os
from crawler.logging import logfunctions
from time import sleep
from multiprocessing import Queue
# from multiprocessing import Pool
from time import time

MAX_BULK_SIZE = 55
data_upload_queue = Queue()


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


def work_queue(db, name, max_req_per_sec):
    starting_time = time()
    while not data_upload_queue.empty():
        try:
            data = data_upload_queue.get()
            try:
                if isinstance(data, list):
                    for r in range(0, len(data), MAX_BULK_SIZE):
                        db.bulk_docs(data[r:r + MAX_BULK_SIZE])
                else:
                    db.create_document(data)
            except HTTPError:
                # put back data and wait
                print 'could not write to db. Sleeping and try again'
                data_upload_queue.put(data)
                sleep(1.0 / max(1, max_req_per_sec - 1))
                work_queue(db)
        except Exception:
            logfunctions.warning('Data queue of {} emptied between check and access'
                                 .format(name))
    return time() - starting_time


class CloudantDB(object):

    def __init__(self, cred_file, db_name):
        self.name = db_name
        self.client = get_client_session(cred_file)
        self.db = self.client.create_database(db_name, throw_on_exists=False)
        self.max_req_per_sec = 10
        # self.db_writer = Pool(processes=1)
        logfunctions.log("Connected to database '{}'".format(db_name))

    def close_session(self):
        if self.client:
            self.client.disconnect()
            logfunctions.log("Disconnected from database '{}'".format(self.name))

    def write_to_db(self, results):
        logfunctions.log("Adding data to writer queue of database '{}'".format(self.name))
        # add data and create a task to work it
        data_upload_queue.put(results)
        # inform pool to work
        # self.db_writer.apply_async(test_async, kwds={'name': self.name,
        #                                              'max_req_per_sec': self.max_req_per_sec})
        return work_queue(self.db, self.name, self.max_req_per_sec)
