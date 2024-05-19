import sys

from log_filters import DebugToWarningLogFilter, ErrorOrCriticalLogFilter


logging_config = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '#%(levelname)-8s [%(asctime)s] - %(message)s'
        },
        'detailed': {
            'format': '#%(levelname)-8s [%(asctime)s] - %(filename)s:'
                      '%(lineno)d - %(name)s:%(funcName)s - %(message)s'
        },
    },
    'filters': {
        'error_critical_filter': {
            '()': ErrorOrCriticalLogFilter,
        },
        'debug_to_warning_filter': {
            '()': DebugToWarningLogFilter,
        }
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'testing': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
            'filters': ['debug_to_warning_filter'],
            'stream': sys.stdout
        },
        'error_file': {
            'class': 'logging.FileHandler',
            'filename': 'errors.log',
            'mode': 'w',
            'formatter': 'detailed',
            'filters': ['error_critical_filter']
        }
    },
    'loggers': {
        'api': {
            'level': 'INFO',
            'handlers': ['error_file']
        },
        'scraper': {
            'level': 'INFO',
            'handlers': ['error_file']
        }
    },
    'root': {
        'formatter': 'default',
        'handlers': ['default']
    }
}
