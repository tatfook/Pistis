import logging
import logging.config

config = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'pistis.log',
            'level': 'INFO',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'root': {
            'handlers': ['console', 'file'],
            'level': 'INFO'
        }
    }
}

logging.config.dictConfig(config)

logger = logging.getLogger('root')
