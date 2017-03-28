#!/usr/bin/env python
"""
    Tests Sendsay API
"""

import os
import unittest
import json
from time import sleep

from sendsay.api import SendsayAPI, attach_file
from test import SendsayTestCase

def data_full_filename(filename):
    """Returns full path to the file in the data directory"""
    return os.path.join(os.path.dirname(__file__), 'data', filename)

def data_from_file(filename):
    """Returns the file content"""
    with open(data_full_filename(filename)) as f:
        return json.loads(f.read())

class TestPing(unittest.TestCase):
    """Test ping requests"""
    def setUp(self):
        self.api = SendsayAPI()

    def test_ping(self):
        """Request ping"""
        self.assertIn('pong', self.api.request('ping').data)

class TestMain(SendsayTestCase):
    """
    Test if SendsayAPI works properly.

    """

    def test_auth(self):
        """Test if authorization works properly"""
        self.api.auth()
        self.assertIsNotNone(self.api.session, msg="auth() doesn't return a session")

        self.api.request('logout')
        self.assertIn('list', self.api.request('sys.settings.get').data,
                      msg="auth() doesn't restore sessions expired")

    def test_request(self):
        """Test of a simple request"""
        self.assertIn('list', self.api.request('sys.settings.get').data,
                      msg="request() doesn't work properly. 'list' is not found in the response")

    def test_attach_file(self):
        """Test if file attaching works correctly"""
        data = data_from_file("test_attach_file.json")
        self.assertEqual(data, attach_file(data_full_filename("img.png")),
                         msg="attach_file() returns a wrong response")

    def test_track(self):
        """Async requests tracking test"""
        if not os.environ['SENDSAY_TEST_EMAIL']:
            raise Exception("SENDSAY_TEST_EMAIL doesn't exist in environmental variables.")

        data = data_from_file("test_track_wait.json")
        response = self.api.request('issue.send', {
            'sendwhen':'now',
            'letter': {
                'subject' : data['letter']['subject'],
                'from.name' : data['letter']['from.name'],
                'from.email': data['letter']['from.email'],
                'message': data['letter']['message'],
                'attaches': [
                    attach_file(x) for x in data['letter']['attaches']
                ],
            },
            'relink' : 1,
            'users.list': os.environ['SENDSAY_TEST_EMAIL'],
            'group' : 'masssending',
        })

        self.assertIn('track.id', response.data,
                      msg="'issue.send' request haven't returned 'track.id'")

        track = response.track
        if track:
            while track.check():
                sleep(5)

        self.assertEqual(track.status, -1, msg="issue.send tracking haven't finished with success")
        self.assertEqual(track.status_message, 'FINISHED_WITH_SUCCESS',
                         msg="issue.send tracking haven't returned a correct status message")


if __name__ == '__main__':
    unittest.main()
