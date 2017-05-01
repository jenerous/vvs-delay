from crawler.crawlerhelpers import monitoring as m

API_NAME = 'monitoring_test_api'

def test():
    failed = False
    monitor = None

    # test get/create monitor
    try:
        monitor = m.get_monitor_for_api(API_NAME)
        if monitor:
            print "Get monitor for Api \t - check"
        else:
            raise
    except:
        failed = True
        print "Get monitor for Api \t - fail"

    # test save monitor
    try:
        called_before = monitor['called']
        monitor['called'] += 1
        m.save(monitor)
        after = m.get_monitor_for_api(API_NAME)
        if after['called'] == called_before + 1:
            print "Safe monitor \t\t\t - check"
        else:
            raise
    except:
        failed = True
        print "Safe monitor \t\t\t - fail"

    # test call duration monitoring
    try:
        monitor = m.get_monitor_for_api(API_NAME)
        monitor['time_consumption'] = [1, 1, 4, 2, 1, 2, 1, 1, 2, 1]
        m.save(monitor)

        m.call_start(API_NAME, 0)
        delayed = m.call_end(API_NAME, 1)
        if delayed:
            raise

        m.call_start(API_NAME, 0)
        delayed = m.call_end(API_NAME, 4)
        if not delayed:
            raise
        print "Duration monitoring \t - check"
    except Exception as e:
        failed = True
        print "Duration monitoring \t - fail"


    return failed


if __name__ == '__main__':
    test()