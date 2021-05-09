import logging
from logging.handlers import TimedRotatingFileHandler

import colorlog
import os


class LoggerFactory:
    @staticmethod
    def getLogger(name: str, folder: str, file: str):
        os.makedirs(folder, exist_ok=True)
        log_colors = {
            "DEBUG": "white",
            "INFO": "green",
            "WARNING": "blue",
            "ERROR": "red",
            "CRITICAL": "red"
        }

        instance = logging.getLogger(name=name)
        instance.setLevel(logging.DEBUG)

        formatter = colorlog.ColoredFormatter(
            '%(asctime)s - [%(levelname)s] - %(filename)s/%(funcName)s:%(lineno)d - %(message)s',
            log_colors=log_colors)
        handler = colorlog.StreamHandler()
        handler.setFormatter(formatter)
        handler.setLevel(logging.WARNING)
        instance.addHandler(handler)

        formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)s] - %(filename)s/%(funcName)s:%(lineno)d - %(message)s'
        )
        filename = os.path.join(folder, file)
        handler = TimedRotatingFileHandler(filename=filename,
                                           when="MIDNIGHT",
                                           interval=1,
                                           backupCount=10,
                                           encoding='utf-8')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        instance.addHandler(handler)

        return instance


logger = LoggerFactory.getLogger(name="webdl-py",
                                 folder="logs",
                                 file="webdl-py.log")
