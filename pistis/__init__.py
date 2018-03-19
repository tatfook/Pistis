from flask import Flask
import unittest

app = Flask(__name__)

@app.cli.command('test')
def test_commmand():
    discover = unittest.defaultTestLoader.discover('.', pattern='*_tests.py')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(discover)

import pistis.views
