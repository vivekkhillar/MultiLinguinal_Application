from .config import config
import os
import logging
from .base_dir import BaseDir
from string import Formatter


class Logger:

    def __init__(self):

        self.BaseDirectory = BaseDir().get_base_directory()
        self.loggerName = config().LOGGER_NAME
        self.loggerLevel = config().LOGGER_LEVEL
        self.environment = config().ENVIRONMENT
        self.logger_path = config().LOGS_PATH
        self.log_dir = os.path.join(self.BaseDirectory,self.logger_path)
        self.log_path = os.path.join(self.log_dir,"app.log")
        self.log_format = "%(process)-5d | %(asctime)s | %(levelname)-2s | %(filename)-8s:%(lineno)-2s | %(funcName)-8s | %(name)-20s | %(message)s"

    def _create_logger_file(self):
        os.makedirs(f'{self.BaseDirectory}/{self.logger_path}',exist_ok=True)
        
    def _build_formatter(self):
        return logging.Formatter(self.log_format)
    
    def _add_console_handler(self,formatter):
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        return handler
    
    def _add_file_handler(self,formatter):
        handler = logging.FileHandler(self.log_path,encoding="utf-8")
        handler.setFormatter(formatter)
        return handler


    def _get_logger(self):

        # create logger path 
        self._create_logger_file()

        # Create a get logger object by using the app name
        logger = logging.getLogger(self.loggerName)
        
        if not logger.handlers:

            # create Formatter object
            formatter = self._build_formatter()

            logger.addHandler(self._add_console_handler(formatter))
            logger.addHandler(self._add_file_handler(formatter))

            logger.setLevel(self.loggerLevel)
        
        return logger


App_logger = Logger()
logger = App_logger._get_logger()