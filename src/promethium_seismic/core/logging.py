# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Logging for the library.

A thin wrapper over the standard library, for one reason: a library that
calls `logging.basicConfig` takes the root logger away from the application
that imported it. This configures only its own named loggers and attaches a
handler once, so a consumer keeps control of everything else.

The level follows the DEBUG setting, so detail is turned on through
configuration rather than by reaching into the logging module.
"""

import logging
import sys
from typing import Any

from promethium_seismic.core.config import get_settings

settings = get_settings()


class CoreLogger:
    """A named logger with a fixed format.

    Attributes:
        logger: The underlying standard library logger.
    """

    def __init__(self, name: str):
        """Build a logger and attach a handler if it has none.

        Args:
            name: The logger name, conventionally the module's `__name__`.

        The handler is attached only when the logger has none. Building the
        same named logger twice is ordinary, and without that check each one
        adds another handler and every message is printed again.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log at INFO.

        Args:
            msg: The message, which may carry printf style placeholders.
            *args: Values for those placeholders.
            **kwargs: Passed to the standard library, for `exc_info` and the
                rest.
        """
        self.logger.info(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log at ERROR.

        Args:
            msg: The message, which may carry printf style placeholders.
            *args: Values for those placeholders.
            **kwargs: Passed to the standard library.
        """
        self.logger.error(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log at WARNING.

        Args:
            msg: The message, which may carry printf style placeholders.
            *args: Values for those placeholders.
            **kwargs: Passed to the standard library.
        """
        self.logger.warning(msg, *args, **kwargs)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log at DEBUG, which is silent unless the DEBUG setting is on.

        Args:
            msg: The message, which may carry printf style placeholders.
            *args: Values for those placeholders.
            **kwargs: Passed to the standard library.
        """
        self.logger.debug(msg, *args, **kwargs)


def get_logger(name: str) -> CoreLogger:
    """Return a logger for a module.

    Args:
        name: The logger name, conventionally the module's `__name__`.

    Returns:
        A logger that writes to standard output in the library's format.
    """
    return CoreLogger(name)


# One logger for code that has no module of its own to name.
logger = get_logger("promethium_seismic")
