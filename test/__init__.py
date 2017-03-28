"""Sandsay test package initialization."""

import os
import unittest
import logging

from sendsay.api import SendsayAPI

class SendsayTestCase(unittest.TestCase):
    """Base class for tests"""
    def setUp(self):
        self.kwargs = {}

        try:
            self.kwargs['login'] = os.environ['SENDSAY_LOGIN']
            self.kwargs['password'] = os.environ['SENDSAY_PASSWORD']
        except KeyError:
            raise Exception("SENDSAY_LOGIN and SENDSAY_PASSWORD should be exist \
                            in environmental variables.")

        if 'SENDSAY_SUBLOGIN' in os.environ:
            self.kwargs['sublogin'] = os.environ['SENDSAY_SUBLOGIN']
        if 'SENDSAY_DEBUG' in os.environ:
            logging.basicConfig()
            logger = logging.getLogger('sendsay.api')
            logger.setLevel(logging.DEBUG)
        if 'SENDSAY_API_URL' in os.environ:
            self.kwargs['api_url'] = os.environ['SENDSAY_API_URL']
        if 'SENDSAY_CERT' in os.environ:
            self.kwargs['cert'] = os.environ['SENDSAY_CERT'].split(',')

        self.api = SendsayAPI(**self.kwargs)

