#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import json
import Queue
import urllib2
import threading

from   time        import sleep
from   time        import time
from   time        import gmtime

from logging       import logfunctions

import settings    as settings

import numpy as np

ONE_MINUTE_IN_SECONDS = 60

class Crawler( object ):
    """
        crawler instance.
        You can plug in different apis which are called by a certain interval
    """
    def __init__( self ):
        self.apis = {}
        self.intervals = {}
        self.db_session = None
        self.db = None
        self.quiet = settings.QUIET

        self.log = logfunctions.log
        self.warning = logfunctions.warning
        self.error = logfunctions.error

    def raw_return( self, result ):
        """
            a very basic function to handle api results. Just return what came
            back from server
            @param result: results from server call
        """
        return result

    def build_get_params( self, data_dict ):
        '''
            function that builds a string with given dict for HTTP get calls
            @params dict that contains key value pairs which chall be concatenated
            @returns string of key value pairs (e.g. 'test1=ok&test2=ok')
        '''
        if len(data_dict.keys()) > 0:
            options = [''] + [(k, data_dict[k]) for k in data_dict]
            return reduce(lambda p1, p2: str(p1) + str(p2[0]) + '=' + str(p2[1]) + '&', options)[:-1]
        else:
            return ''

    def add_api( self, name, url, function_to_call=raw_return, get_params_function={}, interval=5 ):
        """
            add an api to the crawler
            @param name: how shall the api be called. This is like an id!
            @param url: the basic url for the call
            @function_to_call: function that gets called with the results
            @get_params_function: function that gets called to build the api parameters
            @interval: define every x minutes the api shall be called
        """

        # ensure ints and minimum 1
        interval = int(interval) if int(interval) > 0 else 1

        if name in self.apis:
            self.error('API with key "{}" already exists!'.format(name))
            sys.exit(1)
        else:
            # register api
            self.apis[name] = {
                'name': name,
                'url': url,
                'handle': function_to_call,
                'interval': interval,
                'get_params': get_params_function,
                'monitoring': {
                    'called': 0,
                    'time_consumption': [],
                    'errors': 0,
                    'started_last': None
                },
                'queue': Queue.Queue(),
                'threads': None
            }

            # add to timer
            if interval not in self.intervals:
                self.intervals[interval] = []

            self.intervals[interval].append(name)

            self.log('Registered API ' + name, do_print=(not self.quiet))

    def set_db_session(self, client, db_name):
        """
            register db session, open/create database
            @param client: session object
            @param db_name: database name
        """
        self.log("Connected to database " + db_name)
        self.db_session = client
        self.db = client.create_database(db_name, throw_on_exists=False)

    def close_db_session(self):
        """
            disconnect from database
        """
        if self.db_session:
            self.db_session.disconnect()

    def crawl( self, api, timestamp, station ):
        """
            async called api call. Adds results to queue of api
            @param api: api object
            @param timestamp: current time as it comes from time.time
            @param station: id of the station
        """
        self.log(api['name'] + ' was called')
        crawl_params = self.build_get_params(api['get_params'](timestamp, station))
        crawl_results = self.api_call(api['url'] + '?' + crawl_params)
        api['queue'].put({
            'timestamp': timestamp,
            'name': api['name'],
            'station': station,
            'results': crawl_results
        })

    def api_call( self, url ):
        '''
            wrap api calls and return json directly. Rises urllib2.URLError on fail
            @params url url to calls
            @returns json containing the answer
        '''
        try:
            return json.loads(urllib2.urlopen(url).read())
        except urllib2.URLError:
            self.warning('API call failed!\n>' + url, do_print=(not self.quiet))
            return None

    def run( self, SIDs ):
        """
            start the call loop
            @param SIDs: station ids as list
        """

        unique_intervals = np.array(self.intervals.keys(), dtype=np.int)
        unique_intervals = unique_intervals.reshape((1, unique_intervals.shape[0]))
        intervals = np.repeat(unique_intervals, 2, axis=0)
        while True:
            tick = intervals[0].min()
            self.log('sleeping for {} minute{} now\n'.format(tick, 's' if tick > 1 else ''), log=True)
            sys.stdout.flush()

            sleep(tick * ONE_MINUTE_IN_SECONDS)
            intervals[0] = intervals[0] - tick

            call_apis = []

            for i, e in enumerate(intervals[0]):
                if e == 0:
                    for n in self.intervals[intervals[1, i]]:
                        call_apis.append(n)
                    intervals[0, i] = intervals[1, i]

            for n in call_apis:
                timestamp = time()
                self.apis[n]['monitoring']['started_last'] = timestamp
                self.apis[n]['monitoring']['called'] += 1
                self.apis[n]['threads'] = [threading.Thread(target=self.crawl, args=(self.apis[n], gmtime(timestamp), SID, )) for SID in SIDs]
                for t in self.apis[n]['threads']:
                    t.start()

            for n in call_apis:
                for t in self.apis[n]['threads']:
                    t.join()

                # monitoring
                time_needed = time() - self.apis[n]['monitoring']['started_last']
                if self.apis[n]['monitoring']['time_consumption']:
                    time_needed_normally = np.percentile(self.apis[n]['monitoring']['time_consumption'], 80)
                    if time_needed > time_needed_normally:
                        self.warning('{} needed {}. A normal value would be around {}'.format(n, time_needed, time_needed_normally), do_print=(not self.quiet))
                self.apis[n]['monitoring']['time_consumption'].append(time_needed)

                converted_results = self.apis[n]['handle'](self.apis[n]['queue'])
                for c in converted_results:
                    self.db.create_document(c)
