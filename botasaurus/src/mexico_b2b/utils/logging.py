"""
Structured logging module for the Mexico B2B Ingestion Pipeline.
"""

import logging
import sys
from typing import Optional, Any


class StructuredLogger:
    def __init__(self, name: str = "mexico_b2b", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False

        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(level)
            formatter = logging.Formatter(
                fmt="%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _format_kv(self, kwargs: dict) -> str:
        parts = []
        for k, v in kwargs.items():
            if v is not None:
                parts.append(f"{k}={v}")
        return " ".join(parts)

    def info(self, message: Optional[str] = None, **kwargs: Any) -> None:
        formatted = self._format_kv(kwargs)
        full_msg = f"{message} {formatted}".strip() if message else formatted
        self.logger.info(full_msg)

    def warn(self, message: Optional[str] = None, **kwargs: Any) -> None:
        formatted = self._format_kv(kwargs)
        full_msg = f"{message} {formatted}".strip() if message else formatted
        self.logger.warning(full_msg)

    def warning(self, message: Optional[str] = None, **kwargs: Any) -> None:
        self.warn(message, **kwargs)

    def error(self, message: Optional[str] = None, **kwargs: Any) -> None:
        formatted = self._format_kv(kwargs)
        full_msg = f"{message} {formatted}".strip() if message else formatted
        self.logger.error(full_msg)

    def debug(self, message: Optional[str] = None, **kwargs: Any) -> None:
        formatted = self._format_kv(kwargs)
        full_msg = f"{message} {formatted}".strip() if message else formatted
        self.logger.debug(full_msg)


logger = StructuredLogger()
