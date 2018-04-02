class BaseConfig(object):
    STORE_ROOT = 'store'
    JSONIFY_PRETTYPRINT_REGULAR = False
    JOBS = [{
        'id': 'snapshot',
        'func': 'pistis:snapshot',
        'trigger': 'interval',
        'minutes': 10
    }]
    SCHEDULER_API_ENABLED = True

class DebugConfig(BaseConfig):
    STORE_ROOT = 'store_test'
    DEBUG = True

class TestConfig(BaseConfig):
    STORE_ROOT = 'store_test'
    TESTING = True

class ProdConfig(BaseConfig):
    pass

