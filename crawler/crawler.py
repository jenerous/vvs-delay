#!/usr/bin/python
# -*- coding: utf-8 -*-

import Queue
import json
import sys
import threading
import urllib2
from   time import gmtime
from   time import sleep
from   time import time

import numpy as np

import crawlerhelpers.monitoring as monitoring
from config import settings as settings
from logging import logfunctions

ONE_MINUTE_IN_SECONDS = 60

class Crawler( object ):
    """
        crawler instance.
        You can plug in different apis which are called by a certain interval
    """
    def __init__( self ):
        self.apis = {}
        self.intervals = {}
        self.dbs = {}
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
                'queue': Queue.Queue(),
                'threads': None
            }

            # add to timer
            if interval not in self.intervals:
                self.intervals[interval] = []

            self.intervals[interval].append(name)

            self.log('Registered API ' + name, do_print=(not self.quiet))

    def add_db(self, db):
        """
            register db session, open/create database
            @param db: database object
        """
        if db.name in self.dbs:
            self.error('DB with name "{}" already exists!'.format(db.name))
            sys.exit(1)
        else:
            self.dbs[db.name] = db

    def shutdown(self):
        """
            disconnect from databases
        """
        for db in self.dbs.itervalues():
            db.close_session()

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

        for api in self.apis:
            monitoring.register_monitor_for_api(api)

        while True:
            tick = intervals[0].min()
            self.log('sleeping for {} minute{} now\n'.format(tick, 's' if tick > 1 else ''), log=True)
            sys.stdout.flush()

            sleep(tick * ONE_MINUTE_IN_SECONDS)
            intervals[0] = intervals[0] - tick

            call_apis = []

            for i, e in enumerate(intervals[0]):
                if e == 0:
                    for name in self.intervals[intervals[1, i]]:
                        call_apis.append(name)
                    intervals[0, i] = intervals[1, i]

            for name in call_apis:
                timestamp = time()
                monitoring.call_start(name, timestamp)
                self.apis[name]['threads'] = \
                    [threading.Thread(target=self.crawl, args=(self.apis[name], gmtime(timestamp), SID, )) for SID in SIDs]
                for t in self.apis[name]['threads']:
                    t.start()

            for name in call_apis:
                for t in self.apis[name]['threads']:
                    t.join()

                # monitoring
                monitoring.call_end(name, time())

                converted_results = self.apis[name]['handle'](self.apis[name]['queue'])

                if converted_results is not None:
                    for db in self.dbs.itervalues():
                        db.write_to_db(converted_results)
