import logging
from datetime import datetime, timedelta
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
import core.logging_config as lc
from core.logging_config import init_logging, _get_logger, DatedFolderDailyHandler
from core.config import config


@pytest.fixture(autouse=True)
def clean_logger_handlers():
    """Ensure handlers are closed and removed across all loggers, and reset global instance state."""
    cfg = config()
    logger_names = [
        cfg.LOGGER_NAME,
        "test_isolation_logger",
        "test_rollover_logger",
    ]

    def _cleanup():
        lc._app_logger_instance = None
        for name in logger_names:
            log = logging.getLogger(name)
            for handler in list(log.handlers):
                handler.flush()
                handler.close()
                log.removeHandler(handler)
            log.propagate = True

    _cleanup()
    yield
    _cleanup()


def test_logger_initialization():
    """Verify init_logging registers 3 handlers with correct levels and logger name."""
    logger = init_logging()
    cfg = config()

    assert logger.name == cfg.LOGGER_NAME
    assert len(logger.handlers) == 3

    handler_levels = [h.level for h in logger.handlers]
    assert logging.ERROR in handler_levels
    assert _get_logger() is logger


def test_logger_repeated_initialization_no_duplicate_handlers():
    """Verify multiple calls to init_logging do not duplicate handlers."""
    logger_first = init_logging()
    initial_count = len(logger_first.handlers)

    logger_second = init_logging()
    assert logger_second is logger_first
    assert len(logger_second.handlers) == initial_count == 3

def test_logger_initialization_with_pre_existing_handler():
    """Verify behavior when a foreign handler was registered prior to init_logging()."""
    cfg = config()
    raw_logger = logging.getLogger(cfg.LOGGER_NAME)

    # Attach a pre-existing third-party or dummy handler
    pre_existing_handler = logging.NullHandler()
    raw_logger.addHandler(pre_existing_handler)

    assert len(raw_logger.handlers) == 1

    logger = init_logging()

    # Checks whether the pre-existing handler prevented complete initialization
    file_handlers = [
        h for h in logger.handlers if isinstance(h, DatedFolderDailyHandler)
    ]
    assert len(file_handlers) == 2
    assert len(logger.handlers) == 4

def test_logger_handler_types_integration():
    """Verify application and error file handlers are instances of DatedFolderDailyHandler."""
    logger = init_logging()

    file_handlers = [
        h for h in logger.handlers if isinstance(h, DatedFolderDailyHandler)
    ]
    assert len(file_handlers) == 2

    app_handlers = [h for h in file_handlers if h.file_name == "application.log"]
    error_handlers = [h for h in file_handlers if h.file_name == "error.log"]

    assert len(app_handlers) == 1
    assert len(error_handlers) == 1
    assert error_handlers[0].level == logging.ERROR


def test_handler_level_isolation(tmp_path):
    """Verify application.log gets info+error while error.log only captures ERROR."""
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
    """Verify handler creates separate dated folders and writes logs to their respective dates."""
    root_dir = str(tmp_path)
    handler = DatedFolderDailyHandler(root_dir, "application.log")
    handler.setFormatter(logging.Formatter("%(message)s"))

    test_logger = logging.getLogger("test_rollover_logger")
    test_logger.setLevel(logging.INFO)
    test_logger.addHandler(handler)

    # Day 1 log (yesterday)
    yesterday_date = datetime.now() - timedelta(days=1)
    record_day1 = logging.LogRecord(
        name="test_rollover_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Day 1 Log",
        args=(),
        exc_info=None,
    )
    record_day1.created = yesterday_date.timestamp()

    handler.emit(record_day1)
    handler.flush()

    yesterday_str = yesterday_date.strftime("%Y-%m-%d")
    yesterday_log = tmp_path / yesterday_str / "application.log"
    assert yesterday_log.exists()
    assert "Day 1 Log" in yesterday_log.read_text(encoding="utf-8")

    # Day 2 log (today)
    test_logger.info("Day 2 Log")
    handler.flush()

    today_str = datetime.now().strftime("%Y-%m-%d")
    today_log = tmp_path / today_str / "application.log"
    assert today_log.exists()
    assert "Day 2 Log" in today_log.read_text(encoding="utf-8")


def test_dated_folder_rollover_older_timestamp_record(tmp_path):
    """Verify handler switches to an earlier dated folder if an older record arrives."""
    root_dir = str(tmp_path)
    handler = DatedFolderDailyHandler(root_dir, "application.log")
    handler.setFormatter(logging.Formatter("%(message)s"))

    # Emit normal log today
    record_today = logging.LogRecord(
        name="test_rollover_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Today standard log",
        args=(),
        exc_info=None,
    )
    handler.emit(record_today)
    handler.flush()

    # Emit older record (3 days prior)
    past_date = datetime.now() - timedelta(days=3)
    record_past = logging.LogRecord(
        name="test_rollover_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=2,
        msg="Delayed past log",
        args=(),
        exc_info=None,
    )
    record_past.created = past_date.timestamp()

    handler.emit(record_past)
    handler.flush()

    past_date_str = past_date.strftime("%Y-%m-%d")
    past_log = tmp_path / past_date_str / "application.log"
    assert past_log.exists()
    assert "Delayed past log" in past_log.read_text(encoding="utf-8")