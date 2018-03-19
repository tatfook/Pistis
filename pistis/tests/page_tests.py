import os
import pistis
import unittest
import tempfile
import json
import shutil

class PageTestCase(unittest.TestCase):
    def setUp(self):
        pistis.app.testing = True
        pistis.app.config['STORE_ROOT'] = 'store_test'
        self.client = pistis.app.test_client()

    def tearDown(self):
        # shutil.rmtree(pistis.app.config['STORE_ROOT'])
        pass

    def test_page_index(self):
        rv = self.client.get('/')
        self.assertIn(b'index', rv.data)
