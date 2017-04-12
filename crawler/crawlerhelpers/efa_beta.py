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

def function_to_call( results, db ):
    """
        TODO DB SHOULD BE KEEPT SEPERATE
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
    for r in iter(results.get, None):
        db.create_document(r)
