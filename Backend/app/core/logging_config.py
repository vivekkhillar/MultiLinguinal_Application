import os
import logging
from logging.handlers import BaseRotatingHandler
from typing import Optional
from .config import config
from datetime import datetime
from .base_dir import BaseDir

# create Dated Folder Daily Handler cause if server is still up and running then the lifespan will continue in the server
# which will not able to identify and create another date folder for the application and log which will continue in a single folder
# where logging continously appending and make the file size 10 gb or more which we won't able to open file directly 
class DatedFolderDailyHandler(BaseRotatingHandler):

    def __init__(self, root_log_dir: str, file_name: str, encoding: str = "utf-8"):

        self.root_log_dir = root_log_dir
        self.file_name = file_name
        self.current_date_str = datetime.now().strftime("%Y-%m-%d")

        initial_file_path = self._resolve_path(self.current_date_str)
        self._ensure_dir(initial_file_path)

        # delay=False ensures file is created/opened immediately
        super().__init__(initial_file_path, mode="a", encoding=encoding, delay=False)

    def _resolve_path(self, date_str: str) -> str:
        return os.path.join(self.root_log_dir, date_str, self.file_name)

    def _ensure_dir(self, file_path: str) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    def shouldRollover(self, record: logging.LogRecord) -> bool:
        # Check the timestamp of the incoming message against the active handler's date
        record_date_str = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d")
        return record_date_str != self.current_date_str

    def doRollover(self) -> None:
        # 1. Safely flush and close the previous day's open file
        if self.stream:
            self.stream.flush()
            self.stream.close()
            self.stream = None

        # 2. Update to current day's path and create directory
        self.current_date_str = datetime.now().strftime("%Y-%m-%d")
        self.baseFilename = self._resolve_path(self.current_date_str)
        self._ensure_dir(self.baseFilename)

        # 3. Open the fresh day's file stream
        if not self.delay:
            self.stream = self._open()

class Logger:

    def __init__(self):

        cfg = config()
        self.BaseDirectory = BaseDir().get_base_directory()
        self.loggerName = cfg.LOGGER_NAME
        self.environment = cfg.ENVIRONMENT.lower()
        self.logger_path = cfg.LOGS_PATH
        
        # Access Enum value directly
        self.loggerLevel = getattr(logging,cfg.LOGGER_LEVEL.value,logging.INFO)

        # Log directory and dated paths
        self.log_dir = os.path.join(self.BaseDirectory,self.logger_path)
        
        # Fixed: variable name matched to today_dir        
        today_dir = datetime.now().strftime("%Y-%m-%d")
        dated_dir = os.path.join(self.log_dir, today_dir)
        
        self.app_log_path = os.path.join(dated_dir,"application.log")
        self.error_log_path = os.path.join(dated_dir,"error.log")

        # Logging Format
        self.log_format = (f"%(process)-5d | %(asctime)s | {self.environment} | %(levelname)-2s | %(filename)-8s:%(lineno)-2s | %(funcName)-8s | %(name)-20s | %(message)s")
    
    def _ensure_dir(self,file_path : str) -> None: 
        os.makedirs(os.path.dirname(file_path), exist_ok= True)
        
    def _build_formatter(self) -> logging.Formatter:
        return logging.Formatter(self.log_format)
    
    def _add_console_handler(self,formatter : logging.Formatter) -> logging.StreamHandler:
        handler = logging.StreamHandler()
        console_level = logging.INFO if self.environment == "production" else self.loggerLevel
        handler.setLevel(console_level)
        handler.setFormatter(formatter)
        return handler
    
    def _add_app_file_handler(self,formatter : logging.Formatter) -> logging.FileHandler:
        self._ensure_dir(self.app_log_path)
        handler = logging.FileHandler(self.app_log_path,mode= "a",encoding="utf-8")
        handler.setLevel(self.loggerLevel)
        handler.setFormatter(formatter)
        return handler

    def _add_error_file_handler(self,formatter: logging.Formatter) -> logging.FileHandler:
        self._ensure_dir(self.error_log_path)
        handler = logging.FileHandler(self.error_log_path,mode= "a",encoding="utf-8")
        handler.setLevel(logging.ERROR)
        handler.setFormatter(formatter)
        return handler

    def _setup_Logger(self) -> logging.Logger:

        logger = logging.getLogger(self.loggerName)

        if not logger.handlers:
            formatter = self._build_formatter()
            logger.addHandler(self._add_console_handler(formatter))
            logger.addHandler(self._add_app_file_handler(formatter))
            logger.addHandler(self._add_error_file_handler(formatter))

            logger.setLevel(self.loggerLevel)
            logger.propagate = False
        
        return logger


_app_logger_instance : Optional[logging.Logger] = None

def init_logging() -> logging.Logger:
    global _app_logger_instance
    _app_logger_instance = Logger()._setup_Logger()
    return _app_logger_instance

def _get_logger() -> logging.Logger:
    
    global _app_logger_instance
    if _app_logger_instance is None:
        return logging.getLogger(config().LOGGER_NAME)
    return _app_logger_instance
        
