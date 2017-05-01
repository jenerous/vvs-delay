from config import settings
import cloudant_db
from crawler.logging import logfunctions
from numpy import percentile

client = cloudant_db.get_client_session(settings.CLOUDANT_CRED_FILE)
db = client.create_database(settings.MONITORING_DB_NAME, throw_on_exists=False)

monitors = {}

def register_monitor_for_api(api_name):
    monitors[api_name] = get_monitor_for_api(api_name)

def call_start(api_name, timestamp):
    if api_name not in monitors:
        register_monitor_for_api(api_name)

    monitors[api_name]['started_last'] = timestamp
    monitors[api_name]['called'] += 1
    save(monitors[api_name])

def call_end(api_name, timestamp):
    delayed = False
    if api_name not in monitors:
        register_monitor_for_api(api_name)
    time_needed = timestamp - monitors[api_name]['started_last']
    if monitors[api_name]['time_consumption']:
        time_needed_normally = percentile(monitors[api_name]['time_consumption'], 80)
        if time_needed > time_needed_normally:
            delayed = True
            logfunctions.warning(
                '{} needed {}s. A normal value would be around {}s'.format(api_name, time_needed, time_needed_normally))
        monitors[api_name]['time_consumption'].append(time_needed)
    save(monitors[api_name])
    return delayed


def get_monitor_for_api(api_name):
    result = db.get_query_result({'api': {'$eq': api_name}}, raw_result=True)
    if not result['docs']:
        monitor = db.create_document({'api': api_name,
                                      'called': 0,
                                      'time_consumption': [],
                                      'errors': 0,
                                      'started_last': None},
                                     throw_on_exists=True)
    else:
        monitor = db[result['docs'][0]['_id']]
    return monitor

def save(monitor):
    if monitor.exists():
        monitor.save()
    else:
        db.create_document(monitor)
