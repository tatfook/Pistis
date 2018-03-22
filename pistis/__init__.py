from flask import Flask
from flask_apscheduler import APScheduler

import unittest
from dulwich import porcelain as git
import glob
import time

app = Flask(__name__)

@app.cli.command('test')
def test_commmand():
    discover = unittest.defaultTestLoader.discover('.', pattern='*_tests.py')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(discover)


class Config(object):
    STORE_ROOT = 'store'
    JSONIFY_PRETTYPRINT_REGULAR = False
    # set the secret key.  keep this really secret:
    SECRET_KEY = b',\x90\xebYS\xd1\xfa(%\x91s\xf3\x9a\xb9^\xe1x\xf5\xb3\xac\x98\xf7i\xaf\x18V'
    JOBS = [
        {
            'id': 'snapshot',
            'func': 'pistis:snapshot',
            'trigger': 'interval',
            'seconds': 30
        }
    ]
    SCHEDULER_API_ENABLED = True


def job1(a, b):
    print(str(a) + ' ' + str(b))

def snapshot():
    store_root = app.config['STORE_ROOT']
    files = glob.glob('%s/**/*.json'%store_root, recursive=True)
    print(store_root, files)

    git.add(repo=store_root, paths=files)
    print('git add')
    git.commit(repo=store_root, message='manifest snapshot at %s'%(time.strftime("%Y-%m-%d %H:%M:%S %Z%z", time.localtime())))
    print('git commit')


app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)
# scheduler.start()


import pistis.apis
import pistis.views
