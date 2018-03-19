import os
import pistis
import unittest
import tempfile
import json
import shutil

class ApiTestCase(unittest.TestCase):
    def setUp(self):
        pistis.app.testing = True
        pistis.app.config['STORE_ROOT'] = 'store_test'
        self.client = pistis.app.test_client()

    def tearDown(self):
        # shutil.rmtree(pistis.app.config['STORE_ROOT'])
        pass

    def test_add_manifest(self):
        def req(*args, **kwargs):
            res = self.client.post(
                '/api/v1/manifest',
                data=json.dumps(kwargs),
                content_type='application/json',
            )
            return json.loads(res.data.decode())

        self.assertEqual(
            req(fruit='apple', people='adult'),
            dict(error='key "field" not exists')
        )
        self.assertEqual(
            req(field='gitlab'),
            dict(error='unsupported field gitlab')
        )
        self.assertEqual(
            req(field='keepwork'),
            dict(error='incomplete manifest for field keepwork')
        )
        self.assertEqual(
            req(field='keepwork', author='dukes', work='test-report', identity='f844aa8d4ec646c1976a0fde5257767f2387d425'),
            dict(field='keepwork', author='dukes', work='test-report', identity='f844aa8d4ec646c1976a0fde5257767f2387d425')
        )
