import os
import json

# general things
QUIET = False

# DB
DB_NAME = "vvs-delay-db-dev"
CLOUDANT_CRED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vcap-local.json')

# Crawling
APIS = ["efa_beta"]
stations_dir = os.path.dirname(__file__)
STATIONS_FN = os.path.abspath(os.path.join(stations_dir, 'stations.json'))
if os.path.isfile(STATIONS_FN):
    STATION_IDS = json.load(open(STATIONS_FN, 'r'))['stations']
else:
    STATION_IDS = []

# Monitoring
MONITORING_DB_NAME = "monitoring-dev"
