import logging

from colorlog import ColoredFormatter


def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(name)s: %(white)s%(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white'
        })
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    return logger
