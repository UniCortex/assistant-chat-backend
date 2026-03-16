from typing import Any

import structlog
from structlog.types import Processor

from app.setup.config.settings import AppSettings


def configure_logging(settings: AppSettings) -> dict[str, Any]:
    """
    Configure structlog + stdlib logging and return dictConfig for uvicorn.
    """
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.dict_tracebacks,
        structlog.processors.UnicodeDecoder(),
    ]

    structlog.configure(
        processors=[
            *processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    json_formatter: dict[str, Any] = {
        "()": structlog.stdlib.ProcessorFormatter,
        "processor": structlog.processors.JSONRenderer(
            sort_keys=True,
            ensure_ascii=False,
        ),
        "foreign_pre_chain": processors,
    }

    level_name = settings.log_level.upper()

    log_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": json_formatter,
        },
        "handlers": {
            "json": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": level_name,
            "handlers": ["json"],
        },
        "loggers": {
            "uvicorn": {
                "level": level_name,
                "handlers": ["json"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "CRITICAL",
                "handlers": ["json"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": level_name,
                "handlers": ["json"],
                "propagate": False,
            },
        },
    }

    return log_config
