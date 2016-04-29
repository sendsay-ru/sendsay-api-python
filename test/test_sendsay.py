#!/usr/bin/env python
import os
import unittest
import json
from hashlib import md5

from sendsay.api import SendsayAPI, TRACK_STATUSES
from test import SendsayTestCase, show_track_process

def data_full_filename(filename):
    return os.path.join(os.path.dirname(__file__), 'data', filename)

def data_from_file(filename):
    with open(data_full_filename(filename)) as f:
        return json.loads(f.read())

class TestPing(unittest.TestCase):
    def setUp(self):
        self.api = SendsayAPI()

    def test_ping(self):
        self.assertIn('pong', self.api.request('ping'))

class TestMain(SendsayTestCase):
    """
    Test if SendsayAPI works properly.

    """

    def test_auth(self):
        self.api.auth()
        self.assertIsNotNone(self.api.session, msg="auth() doesn't return a session")

        self.api.request('logout')
        self.assertIn('list', self.api.request('sys.settings.get'), msg="auth() doesn't restore the expired session")

    def test_request(self):
        self.assertIn('list', self.api.request('sys.settings.get'), msg="request() doesn't work properly. 'list' is not found in response")

    def test_get_file_content(self):
        data = self.api.get_file_content(data_full_filename("img.png"))
        self.assertEqual(md5(data).hexdigest(), "3bf10d19ebe35253d127c241849c0fca", msg="get_file_content() returns a wrong checksum")

    def test_attach_file(self):
        data = data_from_file("test_attach_file.json")
        self.assertEqual(data, self.api.attach_file(data_full_filename("img.png")), msg="attach_file() returns a wrong response")

    def test_track_wait(self):
        if not os.environ['SENDSAY_TEST_EMAIL']:
            raise Exception("SENDSAY_TEST_EMAIL doesn't exists in environmental variables.")

        data = data_from_file("test_track_wait.json")
        resp = self.api.request('issue.send', {
            'sendwhen':'now',
            'letter': {
                'subject' : data['letter']['subject'],
                'from.name' : data['letter']['from.name'],
                'from.email': data['letter']['from.email'],
                'message': data['letter']['message'],
                'attaches': [
                    self.api.attach_file(x) for x in data['letter']['attaches']
                ],
            },
            'relink' : 1,
            'users.list': os.environ['SENDSAY_TEST_EMAIL'],
            'group' : 'masssending',
        })

        self.assertIn('track.id', resp, msg="'issue.send' request doesn't return 'track.id'")

        result = self.api.track_wait(
            resp,
            callback=show_track_process,
            retry_interval=5,
            max_attempts=100
        )
        self.assertEqual(result, {'status': -1, 'status_msg': 'FINISHED_WITH_SUCCESS'}, msg="track_wait() returns a wrong response")


if __name__ == '__main__':
    unittest.main()
