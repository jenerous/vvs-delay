from time import strftime

def convert_station_id( station_id ):
    """
        convert station id that is given to the api specific
        representation if necessary
        @param station_id: id in general representation
        @return id in api specific representation
    """
    return station_id

def get_name():
    """
        return default name for api
    """
    return 'efaBeta'

def get_base_url():
    """
        return default basic url for api
    """
    return 'https://www3.vvs.de/mngvvs/XML_DM_REQUEST'

def get_params( current_time_raw, station ):
    """
        @param current_time_raw: time as gmtime object
        @param station: station id in general representation
        @return dict with key value pairs for api parameters
    """
    itdDate = strftime("%Y%m%d", current_time_raw)
    itdTime = strftime("%H%M", current_time_raw)

    return {
            'SpEncId' : 0,
            'coordOutputFormat' : "EPSG:4326",
            'deleteAssignedStops' : 1,
            'itdDate' : itdDate,
            'itdTime' : itdTime,
            'limit' : 50,
            'mode' : "direct",
            'name_dm' : "de:8111:{}".format(convert_station_id(station)),
            'outputFormat' : "rapidJSON",
            'serverInfo' : "1",
            'type_dm' : "any",
            'useRealtime' : "1",
            'version' : "10.2.2.48"
        }

def function_to_call( results ):
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
        station = {}
        current_dict = {}
        station[r['station']] = [current_dict]
        current_dict['timestamp'] = r['timestamp']  # "2017-04-14 TEST"
        current_dict['lines'] = {}

        stop_events = filter(lambda elem:
                             elem['transportation']['product']['name']
                             == 'S-Bahn', r['results']['stopEvents'])
        for st_event in stop_events:
            departure_dict = {}
            # print st_event
            if 'isRealtimeControlled' in st_event:
                departure_dict['isRealtimeControlled'] = st_event['isRealtimeControlled']
            else:
                departure_dict['isRealtimeControlled'] = False

            if 'isRealtimeControlled' in departure_dict and 'departureTimeEstimated' in st_event:
                departure_dict['departureTimeEstimated'] = st_event['departureTimeEstimated']
            # else:
            #     departure_dict['departureTimeEstimated'] = None
            departure_dict['departureTimePlanned'] = st_event['departureTimePlanned']
            if 'infos' in st_event:
                departure_dict['infos'] = []
                for i in range(len(st_event['infos'])):
                    info = {}
                    info['content'] = st_event['infos'][i]['content']
                    info['title'] = st_event['infos'][i]['title']
                    info['subtitle'] = st_event['infos'][i]['subtitle']
                    info['properties'] = st_event['infos'][i]['properties']
                    departure_dict['infos'].append(info)
            line = st_event['transportation']['number']
            departure_dict['name'] = st_event['transportation']['product']['name']
            departure_dict['class'] = st_event['transportation']['product']['class']

            if line in current_dict['lines']:
                current_dict['lines'][line].append(departure_dict)
            else:
                current_dict['lines'][line] = [departure_dict]

        converted_results.append(station)
    # print "Results: "
    # with open("results.json", 'w') as output:
    #     json.dump(converted_results, output, indent=4)
    # pprint(converted_results)
