from time import gmtime
from time import strftime


def log(msg, level='INFO', log=False, do_print=True):
    """
        log function, use this instead of direct prints.
        One can also use predefined functions for info, warning and error
        @param msg: the text message that shall be printed
        @param level: prefix for the log message
        @param log: write this to a file or not
        @param do_print: print this to stdout
    """
    current_gmtime = gmtime()
    current_time = strftime('%Y-%m-%d %H:%M:%S', current_gmtime)
    log_msg = '{} [{}]: {}'.format(level, current_time, msg)
    if do_print:
        print log_msg
    if log:
        log_file_name = 'crawler_log_{}.log'.format(strftime('%Y-%m-%d', current_gmtime))
        with open(log_file_name, 'a') as log_file:
            log_file.write(log_msg + '\n')


def warning(msg):
    """
        calls log with WARNING as prefix and log to file activated
        @param msg: the text message that shall be printed
    """
    log(msg, level='WARNING', log=True, do_print=True)


def error(msg):
    """
        Calls log with ERROR as prefix, log to file activated and print to user.
        Terminates the program!
        @param msg: the text message that shall be printed
    """
    log(msg, level='ERROR', log=True, do_print=True)
