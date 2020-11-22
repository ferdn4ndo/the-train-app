import os
import logging

from logging import handlers
from pathlib import Path


class LoggerFolders:
    TESTS = 'tests'
    CONTROLLERS = 'controllers'
    SIMULATIONS = 'simulations'
    COMPARISONS = 'comparisons'


def get_logging_level():
    if os.environ['DEBUG'] != '0':
        return logging.DEBUG
    elif os.environ['ENV_MODE'] == 'dev':
        return logging.INFO
    return logging.WARNING


def get_log_filepath(name, folder: str):
    path = os.path.join(os.environ['LOGS_DIR'], folder)
    Path(path).mkdir(parents=True, exist_ok=True)
    return os.path.join(path, 'CONTROLLER_{}.log'.format(name))


def generate_logger(name: str, folder: str = ""):
    logging_level = get_logging_level()
    logger_name = "_".join([name, folder])
    logger = logging.getLogger(logger_name)

    if len(logger.handlers) > 0:
        return logger

    logger.setLevel(logging_level)

    console_handler = logging.StreamHandler()
    brief_formatter = logging.Formatter('[%(name)s %(levelname)s]: %(message)s')
    console_handler.setFormatter(brief_formatter)
    logger.addHandler(console_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        get_log_filepath(name, folder),
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
    )
    precise_formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    file_handler.setFormatter(precise_formatter)
    logger.addHandler(file_handler)

    return logging.getLogger(logger_name)
