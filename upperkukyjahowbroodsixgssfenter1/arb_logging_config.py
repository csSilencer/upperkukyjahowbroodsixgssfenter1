import logging
import logging.config

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
    },
    'handlers': {
        # Define a file for main process to log to
        'main': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': "arb_main_logs",
            'formatter': 'simple',
        },
        # Define a file for closed group subset monitor to log to
        'macro_arb_logger': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': "macro_arb_logger",
            'formatter': 'simple',
        },
        # Define a file for the arb buy and sell cycle monitors to log to
        'micro_arb_logger': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': "micro_arb_logger",
            'formatter': 'verbose',
        },
        # anything that should be going direct to console
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        }
    },
    'loggers': {
        'main': {
            'handlers': ['main'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'macro_arb_logger': {
            'handlers': ['macro_arb_logger'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'micro_arb_logger': {
            'handlers': ['micro_arb_logger'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'dev_console': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

# logging.config.dictConfig(LOGGING)

# logger = logging.getLogger("dev_console")
# logger.info("dev console")
# logger = logging.getLogger("micro_arb_logger")
# logger.info("micro arb logger")
# logger = logging.getLogger("macro_arb_logger")
# logger.info("macro arb logger")
# logger = logging.getLogger("main")
# logger.info("main logger")