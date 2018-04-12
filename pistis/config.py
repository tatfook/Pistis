class BaseConfig(object):
    JSONIFY_PRETTYPRINT_REGULAR = False
    JOBS = [{
        'id': 'snapshot',
        'func': 'pistis:snapshot',
        'trigger': 'interval',
        'minutes': 10
    }]
    SCHEDULER_API_ENABLED = True

class DebugConfig(BaseConfig):
    STORE_ROOT = 'store'
    DEBUG = True
    TESTING = False

class TestConfig(BaseConfig):
    STORE_ROOT = 'store_test'
    DEBUG = False
    TESTING = True

class ProdConfig(BaseConfig):
    STORE_ROOT = 'store'
    DEBUG = False
    TESTING = False

