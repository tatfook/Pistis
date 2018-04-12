import os
import pistis
import unittest
import tempfile
import json
import shutil

class ApiTestCase(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.client = pistis.app.test_client()

    def tearDown(self):
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

    def test_search_manifest(self):
        def req(*args, **kwargs):
            res = self.client.get(
                '/api/v1/manifest',
                query_string=kwargs
            )
            return json.loads(res.data.decode())

        self.assertEqual(
            req(person='duke', job='test'),
            dict(error='key "field" not exists')
        )
        self.assertEqual(
            req(field='gitlab', location='America'),
            dict(error='unsupported field gitlab')
        )
        self.assertEqual(
            req(field='keepwork', what='the ****'),
            dict(error='incomplete query condition')
        )
        # can't find anything
        self.assertEqual(
            req(field='keepwork', author='aha', work='everhome'),
            dict(data=[])
        )

        # return every version that manifest changes
        self.assertEqual(
            req(field='keepwork', author='duting3', work='haqi'),
            dict(
                data=[
                    dict(
                        manifest=dict(
                            field='keepwork',
                            author='duting3',
                            work='haqi',
                            identity='b0112d212a67c9b3b7e305e53946751fcfcbf4d3'
                        ),
                        pistis=dict(
                            hash='b1beda7644d7b992926d0bfe177baeb25d87872c'
                        ),
                        blockchain=dict(
                            ethereum=dict(
                                hash='e27db291d477391a7556d4467b8c7859609a2200507f950d37cc4b4abf5bb30f'
                            ),
                            bitcoin=dict(
                                hash='f7f5b8d297e8ca4199ad7d2fe82947e449849b53d21804b0a29bb5904fbd0a3f'
                            ),
                        )
                    )
                ]
            )
        )
        self.assertEqual(
            req(field='keepwork', author='keep2', work='paracraft'),
            dict(
                data=[
                    dict(
                        manifest=dict(
                            field='keepwork',
                            author='keep2',
                            work='paracraft',
                            identity='5c1e9ce71b7862d568a75ef5b13562993cc1f9b4'
                        ),
                        pistis=dict(
                            hash='b1beda7644d7b992926d0bfe177baeb25d87872c'
                        ),
                        blockchain=dict(
                            ethereum=dict(
                                hash='e27db291d477391a7556d4467b8c7859609a2200507f950d37cc4b4abf5bb30f'
                            ),
                            bitcoin=dict(
                                hash='f7f5b8d297e8ca4199ad7d2fe82947e449849b53d21804b0a29bb5904fbd0a3f'
                            ),
                        )
                    )
                ]
            )
        )
