"""api module - Classes and methods to interact with Sendsay API"""

import os
import json
import uuid
import base64
import logging
from copy import copy
import requests

from .exceptions import SendsayAPIError, SendsayAPIErrorSessionExpired
from .version import __version__

DEFAULT_API_URL = 'https://api.sendsay.ru'
MAX_ATTEMPTS_REDIRECT = 10
MAX_ATTEMPTS_AUTH = 10

TRACKING_STATUSES = {
    -6: "IS_NOT_MODERATED",
    -5: "ON_MODERATE",
    -4: "WILL_BE_DONE_LATER",
    -3: "CANCELED",
    -2: "FINISHED_WITH_ERROR",
    -1: "FINISHED_WITH_SUCCESS",
    0: "ACCEPTED",
    1: "STARTED",
    2: "IN_PROCESS",
    3: "SORTING",
    4: "FORMATING",
    5: "GENERATING_REPORT",
    6: "CHECKING_FOR_SPAM"
}

LOGGER = logging.getLogger(__name__)

def attach_file(filename, name=None):
    """Read the file and make a proper structure to attach it to an issue"""

    with open(filename, "rb") as content_file:
        content = base64.b64encode(content_file.read())

    return {
        'name': name or os.path.basename(filename),
        'content': content,
        'encoding': 'base64', 'charset': 'utf-8'
    }


class Track(object):
    """
       Class with properties and methods to deal with
       async requests tracking data
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, api, track_id):
        self.api = api
        self.track_id = track_id
        self.data = None
        self.status = None
        self.status_message = None

    def check(self):
        """Get tracking data"""
        response = self.api.request('track.get', dict(id=self.track_id))
        self.data = response.data['obj']
        self.status = int(self.data.get('status'))
        self.status_message = TRACKING_STATUSES[self.status]
        # return True if the process finished
        return self.status >= 0

class Response(object):
    """Class to provide properties and methods to track async requests"""

    # pylint: disable=too-few-public-methods

    def __init__(self, api, data):
        self.api = api
        self.data = data
        self._track = None

    @property
    def track(self):
        """Get an instance of class Track"""
        if 'track.id' in self.data:
            if self._track is None:
                self._track = Track(self.api, self.data['track.id'])
            return self._track

class Sender(object):
    """Class to encapsulate an API request, doing all the required HTTP requests"""

    # pylint: disable=too-few-public-methods

    def __init__(self, api_url=DEFAULT_API_URL, cert=None):
        self.api_url = api_url
        self.cert = cert
        self.redirect_prefix = ''
        self.redirect_attempts = 0

    def request(self, action, params=None):
        """Make a request with redirect"""
        if params is None:
            request_params = {}
        else:
            request_params = copy(params)

        request_params['action'] = action

        post_data = {
            'apiversion' : 100,
            'json' : 1,
            'request' : json.dumps(request_params),
            'request.id' : "sap%s-%s" % (__version__, uuid.uuid4())
        }

        LOGGER.debug('-- request %s, "%s"', self.api_url + self.redirect_prefix, action)
        response = requests.post(self.api_url + self.redirect_prefix, data=post_data,
                                 cert=self.cert)

        # Parse the response as JSON
        try:
            resp_data = response.json()
        except ValueError as error:
            LOGGER.error('-- can not parse "%s"', response.text)
            raise SendsayAPIError([{'id': 'sendsay_api_client/json_parse_error', 'explain': error}])

        # Parse errors
        errors = None

        if 'errors' in resp_data:
            errors = resp_data['errors']
        elif 'error' in resp_data:
            errors = [resp_data['error']]

        if errors:
            for error in errors:
                if error['id'] == 'error/auth/failed' and error['explain'] == 'expired':
                    raise SendsayAPIErrorSessionExpired(errors)
            raise SendsayAPIError(errors)

        # Perform redirect
        if 'REDIRECT' in resp_data:
            if self.redirect_attempts < MAX_ATTEMPTS_REDIRECT:
                self.redirect_prefix = resp_data['REDIRECT']
                self.redirect_attempts += 1
                return self.request(action, params)
            else:
                raise SendsayAPIError([{'id': 'sendsay_api_client/too_many_redirect_attempts'}])

        self.redirect_attempts = 0

        # Success
        return resp_data


class SendsayAPI(object):
    """
        Class to execute API requests with authorization session token,
        helps to attach files and check a result of async requests.
    """

    # pylint: disable=too-many-instance-attributes,too-many-arguments

    def __init__(self, login=None, sublogin=None, password=None,
                 creds_func=None, api_url=DEFAULT_API_URL, cert=None):
        self.session = None
        self.auth_attempts = 0
        self.login = login
        self.sublogin = sublogin or ''
        self.password = password
        self.creds_func = creds_func
        self.sender = Sender(api_url, cert)

    def auth(self):
        """Performs a login request to get a session token"""

        if not self.creds_func:
            (login, sublogin, password) = (self.login, self.sublogin, self.password)
        else:
            (login, sublogin, password) = self.creds_func()

        resp_data = self.sender.request('login',
                                        dict(login=login, sublogin=sublogin, passwd=password))

        if 'session' not in resp_data:
            raise SendsayAPIError([{'id': 'sendsay_api_client/no_session_in_login_response'}])

        self.auth_attempts = 0
        self.session = resp_data['session']

        return self.session

    def request(self, action, params=None):
        """Public method to make an API request"""
        if params is None:
            request_params = {}
        else:
            request_params = copy(params)

        # Get the authorization session
        if (self.login or self.creds_func) and action != 'login':
            request_params['session'] = self.session or self.auth()

        # Make a HTTP request
        try:
            resp_data = self.sender.request(action, request_params)
        except SendsayAPIErrorSessionExpired:
            # The session is wrong or expired
            if self.auth_attempts < MAX_ATTEMPTS_AUTH:
                self.auth_attempts += 1
                self.session = None

                # Try to get a session
                return self.request(action, params)
            else:
                raise SendsayAPIError([{'id': 'sendsay_api_client/too_many_auth_attempts'}])

        # Success
        return Response(self, resp_data)
