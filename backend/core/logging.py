import logging
import sys
from contextvars import ContextVar
from pythonjsonlogger import json as json_log
from config import get_settings

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get("")
        return True


def setup_logging() -> logging.Logger:
    settings = get_settings()
    logger = logging.getLogger("clinical_ka")
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    formatter = json_log.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s",
        rename_fields={"asctime": "timestamp", "levelname": "level"},
    )
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    logger.handlers.clear()
    logger.addHandler(handler)
    return logger


logger = setup_logging()
