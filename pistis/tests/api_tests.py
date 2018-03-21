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
            dict(data=list())
        )
        # manifest not witness by blockchain
        self.assertEqual(
            req(field='keepwork', author='dukes', work='test-report'),
            dict(data=list())
        )

        self.assertEqual(
            req(field='keepwork', author='duting3', work='haqi'),
            dict(
                data=list(
                    dict(
                        manifest=dict(
                            field='keepwork',
                            author='duting3',
                            work='haqi',
                            identity='b0112d212a67c9b3b7e305e53946751fcfcbf4d3'
                        ),
                        pistis=dict(
                            hash='49d8396a7ad575f07df9b65b52f1e36cb7c25738'
                        ),
                        blockchain=dict(
                            ethereum=dict(
                                hash='672ebe4917783964d70c53f88d127ef7610be3414c1372a69a4f08c91ddca1c7'
                            ),
                            bitcoin=dict(
                                hash='6db2becaf27dd73bbf03bed2ab0e7e905299830dbed61a4c1fb34e3be830dd69'
                            ),
                        )
                    )
                )
            )
        )
        self.assertEqual(
            req(field='keepwork', author='keep2', work='paracraft'),
            dict(
                data=list(
                    dict(
                        manifest=dict(
                            field='keepwork',
                            author='keep2',
                            work='paracraft',
                            identity='5c1e9ce71b7862d568a75ef5b13562993cc1f9b4'
                        ),
                        pistis=dict(
                            hash='49d8396a7ad575f07df9b65b52f1e36cb7c25738'
                        ),
                        blockchain=dict(
                            ethereum=dict(
                                hash='672ebe4917783964d70c53f88d127ef7610be3414c1372a69a4f08c91ddca1c7'
                            ),
                            bitcoin=dict(
                                hash='6db2becaf27dd73bbf03bed2ab0e7e905299830dbed61a4c1fb34e3be830dd69'
                            ),
                        )
                    ),
                    dict(
                        manifest=dict(
                            field='keepwork',
                            author='keep2',
                            work='paracraft',
                            identity='5c1e9ce71b7862d568a75ef5b13562993cc1f9b4'
                        ),
                        pistis=dict(
                            hash='8e4d360457898580019ee00700a7ea2ca062fc81'
                        ),
                        blockchain=dict(
                            ethereum=dict(
                                hash='15d879705d8f0b0be12aa4f71255a407e50874583d11d552c93031e8a940dc1d'
                            ),
                            bitcoin=dict(
                                hash='9e409762cce58d92f58723a0d0d3eb1e0cf39316711559c23699b00f6b64b070'
                            ),
                        )
                    )
                )
            )
        )
