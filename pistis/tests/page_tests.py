import os
import pistis
import unittest
import tempfile
import json
import shutil

class PageTestCase(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        pistis.app.testing = True
        pistis.app.config['STORE_ROOT'] = 'store_test'
        self.client = pistis.app.test_client()

    def test_page_index(self):
        rv = self.client.get('/', follow_redirects=True)
        self.assertIn(b'keepwork.com', rv.data)
