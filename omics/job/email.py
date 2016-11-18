"""Email module: Email notificatoin of job information

O/S dependent: Only works on Linux w/ mail command.

emailme: a quick wrapper to send email notification.
watching: a decorator for watching the status of a function by sending an email notification.
"""
import os
import getpass
import platform
import sys
import time
import traceback

def emailme(content, title=None, me=None):
    """Send an email notification to me

    content: text message to send
    title: message title, optional
    me: a user name (yours by default) or a valid email address
    """
    # Use username if none given
    if not isinstance(me, str):
        me = getpass.getuser()
    # Default title if none given
    if not isinstance(title, str):
        server = platform.node()
        pid = os.getpid()
        cwd = os.getcwd()
        title = "Notification from %s: job %d at %s" % (server, pid, cwd)
    # Use O/S mail command
    return os.system("echo '%s' | mail -s '%s' %s" % (content, title, me))


def watching(func):
    """A decorator to capture and report any exception by emailme.
    """
    def decorated(*args, **kwargs):
        try:
            # Run the function
            start_time = time.time()
            results = func(*args, **kwargs)
            end_time = time.time()
            # Elapsed time information
            start_at = time.strftime('%m/%d/%Y %H:%M:%S',
                                     time.localtime(start_time))
            end_at   = time.strftime('%m/%d/%Y %H:%M:%S',
                                     time.localtime(end_time))
            duration = time.strftime('%H:%M:%S',
                                     time.gmtime(end_time - start_time))
            time_info = ['Function: %s' % func.__name__,
                         'Started:  %s' % start_at,
                         'Finished: %s' % end_at,
                         'Duration: %s' % duration]
            # Send a "job done" notification with time info
            emailme('\n'.join(time_info))
            return results
        except:
            # Got exceptions, report the error message via email
            e_type, e_value, e_traceback = sys.exc_info()
            lines = traceback.format_exception(e_type, e_value, e_traceback)
            emailme(''.join(lines))
            raise
    return decorated
