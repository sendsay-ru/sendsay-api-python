import os
import base64
import requests, json, uuid
from copy import copy
from time import sleep
import logging

from exceptions import SendsayAPIError
from version import __version__
DEFAULT_API_URL = 'https://api.sendsay.ru'
MAX_ATTEMPTS_REDIRECT = 10
MAX_ATTEMPTS_AUTH = 10

TRACK_STATUSES = {
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

logger = logging.getLogger(__name__)

class SendsayAPI(object):
    def __init__(self, login=None, sublogin=None, password=None, creds_func=None, api_url=DEFAULT_API_URL, cert=None):
        self.session = None
        self.auth_attempts = 0
        self.redirect_attempts = 0
        self.redirect_prefix = ''
        self.login = login
        self.sublogin = sublogin or ''
        self.password = password
        self.api_url = api_url
        self.creds_func = creds_func
        self.cert = cert

    def get_file_content(self, filename):
        with open(filename, "rb") as content_file:
            return base64.b64encode(content_file.read())

    def attach_file(self, filename, name=None):
        return { 'name': name or os.path.basename(filename), 'content': self.get_file_content(filename), 'encoding': 'base64', 'charset': 'utf-8' }

    def track_wait(self, track_data, callback=None, retry_interval=5, max_attempts=100):
        track_id = None
        if type(track_data) is dict:
            track_id = track_data['track.id']
        elif type(track_data) is str:
            track_id = int(track_data)
        elif type(track_data) is int:
            track_id = track_data

        resp = self.request('track.get', id=track_id)
        status = int(resp['obj']['status'])
        cnt = 0
        while status >= 0:
            resp = self.request('track.get', id=track_id)
            status = int(resp['obj']['status'])
            if callback and callback(resp, status_msg=TRACK_STATUSES[status]):
                break
            if max_attempts and cnt > max_attempts:
                break
            sleep(retry_interval)
            cnt += 1

        return { 'status': status, 'status_msg': TRACK_STATUSES[status] }

    def auth(self):
        # Login request

        if not self.creds_func:
            (login, sublogin, password) = (self.login, self.sublogin, self.password)
        else:
            (login, sublogin, password) = self.creds_func()

        resp_data = self.request('login', login=login, sublogin=sublogin, passwd=password)

        if 'session' not in resp_data:
            raise SendsayAPIError([ { 'id': 'sendsay_api_client/no_session_in_login_response' } ])

        self.auth_attempts = 0
        self.session = resp_data['session']

        return self.session

    def request(self, action, params={}, **kwargs):
        if params == {} and kwargs:
            params = kwargs

        request_params = copy(params)
        request_params['action'] = action

        # Auth
        if (self.login or self.creds_func) and action != 'login':
            request_params['session'] = self.session or self.auth()

        # HTTP request
        post_data = {
            'apiversion' : 100,
            'json' : 1,
            'request' : json.dumps(request_params),
            'request.id' : "sap%s-%s" % (__version__, uuid.uuid4())
        }

        logger.debug('-- request %s, "%s"' % (self.api_url + self.redirect_prefix, action))
        r = requests.post(self.api_url + self.redirect_prefix, data=post_data, cert=self.cert)

        # Parse response as JSON
        try:
            resp_data = r.json()
        except ValueError as e:
            print r.text
            raise SendsayAPIError([ { 'id': 'sendsay_api_client/json_parse_error', 'explain': e } ])

        # Parse errors
        errors = None

        if 'errors' in resp_data:
            errors = resp_data['errors']
        elif 'error' in resp_data:
            errors = [ resp_data['error'] ]

        if errors:
            # Auth expired lookup
            for error in errors:
                if error['id'] == 'error/auth/failed' and error['explain']  == 'expired' and action != 'login':

                    # Session is wrong or expired
                    if self.auth_attempts < MAX_ATTEMPTS_AUTH:
                        self.auth_attempts += 1
                        self.session = None

                        # Try to get session
                        return self.request(action, params)
                    else:
                        raise SendsayAPIError([ { 'id': 'sendsay_api_client/too_many_auth_attempts' } ])

            # Raise exception
            raise SendsayAPIError(errors)

        # Perform redirects
        if 'REDIRECT' in resp_data:
            if self.redirect_attempts < MAX_ATTEMPTS_REDIRECT:
                self.redirect_prefix = resp_data['REDIRECT']
                self.redirect_attempts += 1
                return self.request(action, params)
            else:
                raise SendsayAPIError([ { 'id': 'sendsay_api_client/too_many_redirect_attempts' } ])

        self.redirect_attempts = 0

        # Success
        return resp_data

