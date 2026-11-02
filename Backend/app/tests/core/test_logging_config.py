import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
import pytest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from core.logging_config import init_logging, _get_logger, DatedFolderDailyHandler
from core.config import config


@pytest.fixture(autouse=True)
def clean_logger_handlers():

    cfg = config()
    log = logging.getLogger(cfg.LOGGER_NAME)

    for handler in list(log.handlers):
        handler.close()
        log.removeHandler(handler)

    yield
    
    for handler in list(log.handlers):
        handler.close()
        log.removeHandler(handler)

def test_logger_initialization():
    logger = init_logging()
    cfg = config()
    
    assert logger.name == cfg.LOGGER_NAME
    assert len(logger.handlers) == 3

    handler_levels = [h.level for h in logger.handlers]
    assert logging.ERROR in handler_levels
    assert _get_logger() is logger

def test_handler_level_isolation(tmp_path):

    root_dir = str(tmp_path)
    formatter = logging.Formatter("%(message)s")

    app_handler = DatedFolderDailyHandler(root_dir, "application.log")
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)

    error_handler = DatedFolderDailyHandler(root_dir, "error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    test_logger = logging.getLogger("test_isolation_logger")
    test_logger.setLevel(logging.INFO)
    test_logger.addHandler(app_handler)
    test_logger.addHandler(error_handler)

    test_logger.info("Routine operation log")
    test_logger.error("Critical failure log")

    app_handler.flush()
    error_handler.flush()

    today_str = datetime.now().strftime("%Y-%m-%d")
    app_log = tmp_path / today_str / "application.log"
    error_log = tmp_path / today_str / "error.log"

    assert app_log.exists()
    assert error_log.exists()

    app_content = app_log.read_text(encoding="utf-8")
    error_content = error_log.read_text(encoding="utf-8")

    assert "Routine operation log" in app_content
    assert "Critical failure log" in app_content

    assert "Routine operation log" not in error_content
    assert "Critical failure log" in error_content



def test_dated_folder_rollover_across_days(tmp_path):

    root_dir = str(tmp_path)
    handler = DatedFolderDailyHandler(root_dir,"application.log")
    handler.setFormatter(logging.Formatter("%(message)s"))

    test_logger = logging.getLogger("test_rollover_logger")
    test_logger.setLevel(logging.INFO)
    test_logger.addHandler(handler)

    # Day 1 log
    yesterday_date = datetime.now() -timedelta(days=1)
    record_day1 = logging.LogRecord(
        name = "test", level = logging.INFO, pathname = __file__, lineno=1,
        msg="Day 1 Log", args=(), exc_info=None
    )
    record_day1.created = yesterday_date.timestamp()

    # trigger rollover check
    assert handler.shouldRollover(record_day1) is True
    handler.emit(record_day1)

    test_logger.info("day 2 Log")
    handler.flush()

    today_str = datetime.now().strftime("%Y-%m-%d")
    assert (tmp_path/today_str/"application.log").exists()
    
