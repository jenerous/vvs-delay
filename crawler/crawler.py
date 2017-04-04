#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import Queue
import urllib2
import threading

from   time        import sleep
from   time        import gmtime
from   time        import strftime
from   datetime    import datetime
from   datetime    import date

import numpy as np

ONE_MINUTE_IN_SECONDS = 60

class Crawler( object ):
    """

    """
    def __init__( self ):
        self.apis = {}
        self.intervals = {}

    def raw_return( self, results ):
        return results

    def build_get_params( self, data_dict ):
        '''
            function that builds a string with given dict for HTTP get calls
            @params dict that contains key value pairs which chall be concatenated
            @returns string of key value pairs (e.g. 'test1=ok&test2=ok')
        '''
        if len(data_dict.keys) > 0:
            options = [''] + [(k, data_dict[k]) for k in data_dict]
            return reduce(lambda p1, p2: str(p1) + str(p2[0]) + '=' + str(p2[1]) + '&', options)[:-1]
        else:
            return ''

    def add_api( self, name, url, function_to_call=raw_return, get_params_function={}, interval=5 ):
        # ensure ints and minimum 1
        interval = int(interval) if int(interval) > 0 else 1

        if name in self.apis:
            print 'API with key "{}" already exists!'.format(name)
            sys.exit(1)
        else:
            # register api
            self.apis[name] = {
                'name': name,
                'url': url,
                'call': function_to_call,
                'interval': interval,
                'get_params': get_params_function
            }

            # add to timer
            if interval not in self.intervals:
                self.intervals[interval] = []

            self.intervals[interval].append(name)

    def crawl( self, api, timestamp ):
        print api['name'], 'was called at {}'.format(strftime('%H:%M:%S', timestamp))

    def run( self ):
        unique_intervals = np.unique([self.apis[x]['interval'] for x in self.apis])
        unique_intervals = unique_intervals.reshape((1, unique_intervals.shape[0]))
        intervals = np.repeat(unique_intervals, 2, axis=0)

        while True:
            tick = intervals[0].min()
            print 'sleeping for {} minutes now'.format(tick)
            sys.stdout.flush()
            sleep(tick * ONE_MINUTE_IN_SECONDS)

            intervals[0] = intervals[0] - tick

            for i, e in enumerate(intervals[0]):
                if e == 0:
                    for n in self.intervals[intervals[1, i]]:
                        timestamp = gmtime()
                        self.crawl(self.apis[n], timestamp)
                    intervals[0, i] = intervals[1, i]

#
# DEBUG = True
#
# # set Hauptbahnhof as an entry point
# ENTRY_POINT_ID = '5006008'
# API_EFA        = {
#     'base': 'https://efa-api.asw.io/api/v1/',
#     'station': None
# }
#
# API_VVS        = {
#     'base': "http://mobil.vvs.de/jqm/controller/XSLT_",
#     'geo': None,
#     'params_geo': {
#         'hideBannerInfo': 1,
#         'coordListOutputFormat': "STRING",
#         'filterEpsilon': "5.0",
#         'returnSinglePath': "1",
#         'command': "bothdirections",
#         'outputFormat': "JSON",
#         'stFaZon': 1,
#         'spTZO': 1,
#         'lineReqType': "DM"
#     }
# }
#
#
# def represents_int(s):
#     ''' Check if s is an int
#         @params s value to check
#         @returns True if s is an int else False
#     '''
#     try:
#         int(s)
#         return True
#     except ValueError:
#         return False
#
#
# def build_get_params(data_dict):
#     '''
#         function that builds a string with given dict for HTTP get calls
#         @params dict that contains key value pairs which chall be concatenated
#         @returns string of key value pairs (e.g. 'test1=ok&test2=ok')
#     '''
#     options = [''] + [(k, data_dict[k]) for k in data_dict]
#     return reduce(lambda p1, p2: str(p1) + str(p2[0]) + '=' + str(p2[1]) + '&', options)[:-1]
#
#
# def api_call(url):
#     '''
#         wrap api calls and return json directly. Rises urllib2.URLError on fail
#         @params url url to calls
#         @returns json containing the answer
#     '''
#     try:
#         return json.loads(urllib2.urlopen(url).read())
#     except urllib2.URLError:
#         print 'API call failed!'
#         print '>', url
#         return None
#
#
# def update_api_urls():
#     '''
#         sets the urls of the global API dictionary
#     '''
#     # EFA API
#     api_options = api_call(API_EFA['base'])
#     if api_options is not None:
#         API_EFA['station'] = api_options['station']
#
#     # VVS API
#     API_VVS['geo'] = API_VVS['base'] + 'GEOOBJECT_REQUEST?' + build_get_params(API_VVS['params_geo'])
#
#
# def get_stations():
#     '''
#         get all available stations from EFA API
#         @returns list of station ids
#     '''
#     update_api_urls()
#     stations          = api_call(API_EFA['station'])
#     filtered_stations = filter(lambda s: represents_int(s['stationId']), stations)
#
#     return filtered_stations
#
#
# def crawl_station( SID, queue ):
#     '''
#         crawl the departure information of a station given by its id.
#         This is a helper function of crawl_station_parallel
#     '''
#     departures_dict   = api_call("{}/departures".format(os.path.join(API_EFA['station'], SID)))
#     print 'crawling {}'.format(SID)
#     queue.put(departures_dict)
#
#
# def crawl_station_parallel( SIDs ):
#     '''
#         crawl departure information from different stations
#         @params SIDs list of station ids to crawl
#     '''
#     result  = Queue.Queue()
#     threads = [threading.Thread(target=crawl_station, args=(SID, result)) for SID in SIDs]
#     for t in threads:
#         t.start()
#     for t in threads:
#         t.join()
#     return result
#
#
# def crawl_all(interval=60, stations=None):
#     '''
#         build a list of station ids and crawl departure information of those
#         @param interval: seconds to sleep between calls
#     '''
#     if stations is None:
#         all_stations        = get_stations()
#         all_station_ids     = map(lambda s: s['stationId'], all_stations)
#     else:
#         all_station_ids    = stations
#
#     all_stations_amount = len(all_station_ids)
#     print all_stations_amount, 'stations'
#     raw_input('proceed?')
#     while True:
#         current_time_raw = gmtime()
#         current_time     = strftime("%Y-%m-%d_%H-%M-%S", current_time_raw)
#         output           = {}
#         results          = crawl_station_parallel(all_station_ids)
#         for r in results:
#             output[SID]            = {}
#             output[SID]['data']    = r
#             output[SID]['time']    = current_time
#             output[SID]['station'] = r['stationId']
#
#         print 'saving', current_time
#         with open('{}.json'.format(current_time), 'w') as out:
#             out.write(json.dumps(output))
#
#         took_time  = gmtime() - current_time_raw
#         print 'took_time', took_time
#         sleep_time = interval - took_time
#         if sleep_time < 0:
#             print 'You could think of increasing your interval.'
#             print 'Crawling took {} seconds, interval is {} seconds'.format(took_time, interval)
#
#         print 'sleeping for {} seconds'.format(max(0, sleep_time))
#         sleep(max(0, sleep_time))
#
#
# def get_line_details(line):
#     year = str(date.today().year)[-2:]
#     l    = '&line=vvs%3A1{:0>4}%3A+%3AH%3Aj{}'.format(line, year)
#     line_details_dict = api_call("{}{}".format(API_VVS['geo'], l))
#
#     with open('{}.json'.format('selischs.json'), 'w') as out:
#         out.write(json.dumps(line_details_dict, indent=1))
#
#
#     if DEBUG and line_details_dict is not None:
#         for item in line_details_dict['geoObjects']['items']:
#             print
#             print '#' * 80
#             print item['item']['points'][0]['name'], '->', item['item']['points'][-1]['name']
#             print '#' * 80
#
#             for i in item['item']['points']:
#                 print i['ref']['id'], i['name']
#
#     return_list = []
#
#     if line_details_dict is not None:
#         for i in range(len(line_details_dict['geoObjects']['params']['modes'])):
#
#             line_dict = {
#                 'line': line_details_dict['geoObjects']['params']['modes'][i]['mode']['symbol'],
#                 'direction': {
#                     'id': line_details_dict['geoObjects']['params']['modes'][i]['mode']['destID'],
#                     'name': line_details_dict['geoObjects']['params']['modes'][i]['mode']['destination'],
#                     'direction_indicator':  line_details_dict['geoObjects']['params']['modes'][i]['mode']['diva']['dir']
#                 },
#                 'point_ids': [(p['ref']['id'], p['ref']['platform']) for p in line_details_dict['geoObjects']['items'][i]['item']['points']]
#             }
#
#             return_list.append(line_dict)
#
#     return return_list


def main():
    # update_api_urls()
    #
    # s1 = get_line_details('1')
    # s2 = get_line_details('2')
    # s3 = get_line_details('3')
    #
    # dump = [s1, s2, s3]
    # print dump
    # with open('dump123.json', 'w') as out:
    #     if DEBUG:
    #         out.write(json.dumps(dump, indent=2))
    #     else:
    #         out.write(json.dumps(dump))
    #
    # for direction in s1:
    #     print direction

    # crawl_all(stations=[ENTRY_POINT_ID, '5004853'])




    def efaBeta_params():
        current_time_raw = gmtime()
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
            'name_dm' : "de:8111:6008",
            'outputFormat' : "rapidJSON",
            'serverInfo' : "1",
            'type_dm' : "any",
            'useRealtime' : "1",
            'version' : "10.2.2.48"
        }

    crawler = Crawler()
    crawler.add_api( 'EFABeta', 'https://www3.vvs.de/mngvvs/XML_DM_REQUEST', get_params_function=efaBeta_params)
    crawler.add_api( 'EFABeta2', 'https://www3.vvs.de/mngvvs/XML_DM_REQUEST', get_params_function=efaBeta_params, interval=2)
    crawler.add_api( 'EFABeta3', 'https://www3.vvs.de/mngvvs/XML_DM_REQUEST', get_params_function=efaBeta_params, interval=9)
    crawler.run()


if __name__ == "__main__":
    main()
