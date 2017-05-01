import os

# general things
QUIET = False

# DB
DB_NAME = "vvs-delay-db"
CLOUDANT_CRED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vcap-local.json')

# Crawling
APIS = ["efa_beta"]
STATION_IDS = ['6008']

# Monitoring
MONITORING_DB_NAME = "monitoring-dev"