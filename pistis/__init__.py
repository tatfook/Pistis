from flask import Flask
from flask_apscheduler import APScheduler

import unittest
import glob
import time
from pistis.log import logger
from pistis.config import DebugConfig, TestConfig, ProdConfig
from os import environ
from git import Repo


app = Flask(__name__)

env = environ.get('PISTIS_ENV')
if env == 'DEBUG':
    app.config.from_object(DebugConfig())
elif env == 'TEST':
    app.config.from_object(TestConfig())
else:
    app.config.from_object(ProdConfig())


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
    git.push('origin', 'master')
    logger.info('sync with github server')


scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
logger.info('create git snapshot scheduler')

import pistis.apis
import pistis.views
