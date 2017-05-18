def get_instance():
    return API_test()


class API_test(object):
    """testing API class"""
    def __init__(self):
        self.name = 'TEST'
        self.baseurl = 'https://127.0.0.1'

    def convert_station_id(self, station_id):
        """
            convert station id that is given to the api specific
            representation if necessary
            @param station_id: id in general representation
            @return id in api specific representation
        """
        return station_id

    def get_name(self):
        """
            return default name for api
        """
        return ''

    def get_base_url(self):
        """
            return default basic url for api
        """
        return ''

    def get_params(self, current_time_raw, station):
        """
            @param current_time_raw: time as gmtime object
            @param station: station id in general representation
            @return dict with key value pairs for api parameters
        """
        return {
            'test': 'test'
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
            pass
