"""
Most of the functions needed by the web service are here. 
In run_app.py we just keep the main web logic.
"""
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import str

import datetime
import json

class FlaskRedirectException(Exception):
    """
    Class used to return immediately with a flash message and a redirect.
    """
    pass


MAX_NUMBER_OF_ATOMS = 1000
time_reversal_note = ("The second half of the path is required only if "
                      "the system does not have time-reversal symmetry")


def logme(logger, *args, **kwargs):
    """
    Log information on the passed logger. 

    See docstring of generate_log for more info on the
    accepted kwargs.

    :param logger: a valid logger. If you pass `None`, no log is output.
    """
    if logger is not None:
        logger.debug(generate_log(*args, **kwargs))


def generate_log(filecontent,
                 fileformat,
                 request,
                 call_source,
                 reason,
                 extra={}):
    """
    Given a string with the file content, a file format, a Flask request and 
    a string identifying the reason for logging, stores the 
    correct logs.

    :param filecontent: a string with the file content
    :param fileformat: string with the file format
    :param request: a Flask request
    :param call_source: a string identifying who called the function
    :param reason: a string identifying the reason for this log
    :param extra: additional data to add to the logged dictionary. 
        NOTE! it must be JSON-serializable
    """
    # I don't know the fileformat
    data = {'filecontent': filecontent, 'fileformat': fileformat}

    logdict = {
        'data': data,
        'reason': reason,
        'request': str(request.headers),
        'call_source': call_source,
        'source': request.headers.get('X-Forwarded-For', request.remote_addr),
        'time': datetime.datetime.now().isoformat()
    }
    logdict.update(extra)
    return json.dumps(logdict)


def process_data_core(module_version="",
                           call_source="",
                           logger=None,
                           flask_request=None):
    """
    The main function that generates the data to be sent back to the view.

    :param module_version: the module. The reason for passing it
         is that, when running in debug mode, you want to get the local 
         app rather than the installed one.
    :param call_source: a string identifying the source (i.e., who called
       this function). This is a string, mainly for logging reasons.
    :param logger: if not None, should be a valid logger, that is used
       to output useful log messages.
    :param flask_request: if logger is not None, pass also the flask.request
       object to help in logging.

    :return: this function calls directly flask methods and returns flask 
        objects

    :raise: FlaskRedirectException if there is an error that requires
        to redirect the the main selection page. The Exception message
        is the message to be flashed via Flask (or in general shown to
        the user).
    """
    return {"data": "Processed data information..."}

