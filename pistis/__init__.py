from flask import Flask
from flask_apscheduler import APScheduler

import unittest
import glob
import time
from pistis.log import logger
from os import environ

from git import Repo


class Config(object):
    JSONIFY_PRETTYPRINT_REGULAR = False
    JOBS = [{
        'id': 'snapshot',
        'func': 'pistis:snapshot',
        'trigger': 'interval',
        'minutes': 10
    }]
    SCHEDULER_API_ENABLED = True


app = Flask(__name__)
app.config.from_object(Config())

if environ.get('PISTIS_SETTINGS') is not None:
    app.config.from_envvar('PISTIS_SETTINGS')


repo = Repo(app.config['STORE_ROOT'])
git = repo.git


@app.cli.command('test')
def test_commmand():
    discover = unittest.defaultTestLoader.discover('.', pattern='*_tests.py')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(discover)


def snapshot():
    git.add('.')
    git.commit('--allow-empty', '-m',
               'manifest snapshot at %s' % (time.strftime("%Y-%m-%d %H:%M:%S %Z%z", time.localtime())))

    logger.info('create new git commit')


scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
logger.info('create git snapshot scheduler')

import pistis.apis
import pistis.views
