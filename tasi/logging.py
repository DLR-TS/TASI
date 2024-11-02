"""
Module to setup printing logging messages in a multiprocessing environment
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

import coloredlogs

MSG_TEMPLATE = "[%(asctime)s | %(filename)s:%(funcName)s:%(lineno)d] > %(levelname)s:  %(message)s"

LOGGER = "tasi"


def init_logger(console_level: int = logging.INFO, file_level: int = logging.DEBUG, filename: str = None):

    # get the current root logger
    logger = logging.getLogger()

    # create a format for the logging. For file logging as well as for logging to console
    log_format = logging.Formatter(MSG_TEMPLATE.format(start="", end=""))

    # set the default log level to the console level
    logger.setLevel(console_level)

    if filename:
        # setup a rotating file logger
        file_handler = RotatingFileHandler(filename, pow(2, 20), 10, delay=True)
        file_handler.setFormatter(log_format)
        file_handler.setLevel(file_level)
        logger.addHandler(file_handler)

    # setup the console logging - log to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(coloredlogs.ColoredFormatter(fmt=MSG_TEMPLATE))
    handler.setLevel(console_level)
    logger.addHandler(handler)
