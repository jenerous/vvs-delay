from time import strftime
from time import gmtime


def get_instance():
    return API_efaBeta()


class API_efaBeta(object):
    def __init__(self):
        self.name = 'efaBeta'
        self.baseurl = 'https://www3.vvs.de/mngvvs/XML_DM_REQUEST'
        self.version = '1.3'

    def convert_station_id(self, station_id):
        """
            convert station id that is given to the api specific
            representation if necessary
            @param station_id: id in general representation
            @return id in api specific representation
        """
        return station_id[3:]

    def get_params(self, current_time_raw, station):
        """
            @param current_time_raw: seconds from time.time
            @param station: station id in general representation
            @return dict with key value pairs for api parameters
        """
        itdDate = strftime("%Y%m%d", gmtime(current_time_raw / 1000.0))
        itdTime = strftime("%H%M", gmtime(current_time_raw / 1000.0))
        return {
                'SpEncId': 0,
                'coordOutputFormat': "EPSG:4326",
                'deleteAssignedStops': 1,
                'itdDate': itdDate,
                'itdTime': itdTime,
                'limit': 50,
                'mode': "direct",
                'name_dm': "de:8111:{}".format(self.convert_station_id(station)),
                'outputFormat': "rapidJSON",
                'serverInfo': "1",
                'type_dm': "any",
                'useRealtime': "1",
                'version': "10.2.2.48"
            }

    def function_to_call(self, results):
        """
            function that gets called on an api response
            @param results: queue object of the api that contains result dicts from
            the api call.
            {
                'timestamp': gmtime object -> when was the api call made
                'name': api's name (id),
                'station': station id,
                'results': crawl results -> what came back from api
            }
        """
        results.put(None)
        converted_results = []

        for r in iter(results.get, None):
            r['version'] = self.version

            current_dict = {
                'lines': {}
            }

            if 'results' not in r or 'stopEvents' not in r['results']:
                continue

            product_types = ['S-Bahn']
            # only use S-Bahn and realtime controlled
            stop_events = filter(lambda elem:
                                 elem['transportation']['product']['name'] in product_types
                                 and 'isRealtimeControlled' in elem,
                                 r['results']['stopEvents'])

            for st_event in stop_events:
                departure_dict = {}

                if 'departureTimeEstimated' in st_event:
                    departure_dict['departureTimeEstimated'] = st_event['departureTimeEstimated']
                # else:
                #     departure_dict['departureTimeEstimated'] = None
                departure_dict['departureTimePlanned'] = st_event['departureTimePlanned']
                if 'infos' in st_event:
                    departure_dict['infos'] = []
                    for i in range(len(st_event['infos'])):
                        info = {}
                        if 'content' in st_event['infos'][i]:
                            info['content'] = st_event['infos'][i]['content']
                        else:
                            info['content'] = ""

                        info['title'] = st_event['infos'][i]['title']
                        info['subtitle'] = st_event['infos'][i]['subtitle']
                        info['properties'] = st_event['infos'][i]['properties']
                        departure_dict['infos'].append(info)
                line = st_event['transportation']['number']
                departure_dict['name'] = st_event['transportation']['product']['name']
                departure_dict['class'] = st_event['transportation']['product']['class']
                departure_dict['class'] = st_event['transportation']['product']['class']
                departure_dict['id'] = st_event['transportation']['product']['id']

                if line in current_dict['lines']:
                    current_dict['lines'][line].append(departure_dict)
                else:
                    current_dict['lines'][line] = [departure_dict]

            r['results'] = current_dict
            converted_results.append(r)

        return converted_results
