import os
import logging
from datetime import datetime
from logging.handlers import BaseRotatingHandler
from typing import Optional
from .config import config
from .base_dir import BaseDir


class DatedFolderDailyHandler(BaseRotatingHandler):
    """
    Rotates log files across date changes into dated directories:
    <root_log_dir>/YYYY-MM-DD/<file_name>
    """
    def __init__(self, root_log_dir: str, file_name: str, encoding: str = "utf-8"):
        self.root_log_dir = root_log_dir
        self.file_name = file_name
        self.current_date_str = datetime.now().strftime("%Y-%m-%d")
        self._target_date_str: Optional[str] = None

        initial_file_path = self._resolve_path(self.current_date_str)
        self._ensure_dir(initial_file_path)

        super().__init__(initial_file_path, mode="a", encoding=encoding, delay=False)

    def _resolve_path(self, date_str: str) -> str:
        return os.path.join(self.root_log_dir, date_str, self.file_name)

    def _ensure_dir(self, file_path: str) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    def shouldRollover(self, record: logging.LogRecord) -> bool:
        record_date_str = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d")
        if record_date_str != self.current_date_str:
            self._target_date_str = record_date_str
            return True
        return False

    def doRollover(self, target_date: Optional[str] = None) -> None:
        if self.stream:
            self.stream.flush()
            self.stream.close()
            self.stream = None

        # Prefer explicitly supplied date or record date over clock fallback
        new_date = target_date or self._target_date_str or datetime.now().strftime("%Y-%m-%d")
        self.current_date_str = new_date
        self._target_date_str = None

        self.baseFilename = self._resolve_path(self.current_date_str)
        self._ensure_dir(self.baseFilename)

        if not self.delay:
            self.stream = self._open()


class Logger:

    def __init__(self):
        cfg = config()
        self.BaseDirectory = BaseDir().get_base_directory()
        self.loggerName = cfg.LOGGER_NAME
        self.environment = cfg.ENVIRONMENT.upper()
        self.logger_path = cfg.LOGS_PATH

        self.loggerLevel = getattr(logging, cfg.LOGGER_LEVEL.value, logging.INFO)
        self.log_dir = os.path.join(self.BaseDirectory, self.logger_path)

        self.log_format = (
            f"%(process)-5d | %(asctime)s | %(levelname)-2s | "
            f"%(filename)-8s:%(lineno)-2s | %(funcName)-8s | "
            f"%(name)-20s | [{self.environment}] | %(message)s"
        )

    def _build_formatter(self) -> logging.Formatter:
        return logging.Formatter(self.log_format)

    def _add_console_handler(self, formatter: logging.Formatter) -> logging.StreamHandler:
        handler = logging.StreamHandler()
        console_level = logging.INFO if self.environment == "PRODUCTION" else self.loggerLevel
        handler.setLevel(console_level)
        handler.setFormatter(formatter)
        return handler

    def _add_app_file_handler(self, formatter: logging.Formatter) -> DatedFolderDailyHandler:
        handler = DatedFolderDailyHandler(
            root_log_dir=self.log_dir,
            file_name="application.log"
        )
        handler.setLevel(self.loggerLevel)
        handler.setFormatter(formatter)
        return handler

    def _add_error_file_handler(self, formatter: logging.Formatter) -> DatedFolderDailyHandler:
        handler = DatedFolderDailyHandler(
            root_log_dir=self.log_dir,
            file_name="error.log"
        )
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


_app_logger_instance: Optional[logging.Logger] = None


def init_logging() -> logging.Logger:
    global _app_logger_instance
    if _app_logger_instance is None or not _app_logger_instance.handlers:
        _app_logger_instance = Logger()._setup_Logger()
    return _app_logger_instance


def _get_logger() -> logging.Logger:
    global _app_logger_instance
    if _app_logger_instance is None:
        return logging.getLogger(config().LOGGER_NAME)
    return _app_logger_instance