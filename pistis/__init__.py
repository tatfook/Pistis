from flask import Flask
from flask_apscheduler import APScheduler

import unittest
from dulwich import porcelain as git
import glob
import time
from pistis.log import logger


class Config(object):
    STORE_ROOT = 'store'
    JSONIFY_PRETTYPRINT_REGULAR = False
    # set the secret key. keep this really secret:
    SECRET_KEY = b',\x90\xebYS\xd1\xfa(%\x91s\xf3\x9a\xb9^\xe1x\xf5\xb3\xac\x98\xf7i\xaf\x18V'
    JOBS = [{
        'id': 'snapshot',
        'func': 'pistis:snapshot',
        'trigger': 'interval',
        'minutes': 10
    }]
    SCHEDULER_API_ENABLED = True


app = Flask(__name__)
app.config.from_object(Config())

repo = git.Repo(app.config['STORE_ROOT'])


@app.cli.command('test')
def test_commmand():
    discover = unittest.defaultTestLoader.discover('.', pattern='*_tests.py')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(discover)


def snapshot():
    store_root = app.config['STORE_ROOT']
    files = glob.glob('%s/**/*.json' % store_root, recursive=True)

    git.add(repo=store_root, paths=files)

    git.commit(
        repo=store_root,
        message='manifest snapshot at %s' %
        (time.strftime("%Y-%m-%d %H:%M:%S %Z%z", time.localtime())))
    logger.info('create new git commit')


scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
logger.info('create git snapshot scheduler')

import pistis.apis
import pistis.views
