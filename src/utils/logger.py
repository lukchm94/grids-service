from __future__ import annotations

import logging
import sys
from logging import Logger

from __app_configs import Env, LoggerConfig


def get_cloudwatch_logger(env: str = Env.dev.value) -> Logger:
    logger = logging.getLogger(LoggerConfig.log_name.value)
    logger.setLevel(
        LoggerConfig.default_level.value
        if env == Env.prod.value
        else LoggerConfig.debug.value
    )

    logFormat = logging.Formatter(
        "[%(name)s] - %(asctime)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logFormat)
    logger.addHandler(console_handler)
    return logger


logger: Logger = get_cloudwatch_logger()
