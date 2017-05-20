import threading
from crawler.crawler import Crawler
from time import gmtime
from time import strftime
from time import strptime
import os


def test():
    failed = False
    try:
        # get a crawler instance
        mycrawler = Crawler()
        print "Crawler instance \t - check"
    except Exception as e:
        failed = True
        print "Crawler instance \t - fail"
        print e

    try:
        # add an api
        from crawler.crawlerhelpers.test_api import API_test
        api_test = API_test()
        mycrawler.add_api(api_test.name, api_test.baseurl,
                          get_params_function=api_test.get_params,
                          function_to_call=api_test.function_to_call)
        print "add api \t\t - check"
    except Exception as e:
        failed = True
        print "add api \t\t - failed"
        print e

    try:
        # double add api
        time_before_thread_call = gmtime()

        api_test_2 = API_test()
        add2 = threading.Thread(target=mycrawler.add_api,
                                args=(api_test_2.name, api_test_2.baseurl),
                                kwargs={'get_params_function': api_test_2.get_params,
                                        'function_to_call':  api_test_2.function_to_call})
        add2.start()
        add2.join()

        log_file_name = 'crawler_log_{}.log'.format(strftime('%Y-%m-%d', time_before_thread_call))
        this_failed = True
        # that's not the best solution I guess, but yeah... should work
        # check the logfile for error message
        if os.path.isfile(log_file_name):
            with open(log_file_name, 'r') as log_file:
                for l in log_file:
                    if l.startswith('ERROR'):
                        time_str = l[len('ERROR ['):l.index(']')]
                        if strptime(strftime('%Y-%m-%d %H:%M:%S', time_before_thread_call),
                                    '%Y-%m-%d %H:%M:%S') <= strptime(time_str, '%Y-%m-%d %H:%M:%S'):
                            if l.strip().endswith('API with key "TEST" already exists!'):
                                print "add api twice \t\t - check"
                                this_failed = False

        else:
            print 'no log file!'
        if this_failed:
            failed = True
            print "add api twice \t\t - failed"
    except Exception as e:
        failed = True
        print "add api twice \t\t - failed"
        print e

    return failed


if __name__ == '__main__':
    test()
