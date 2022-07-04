"""api/helper/__init__.py"""
import sys
from loguru import logger

LOGGER_CONFIG = {
    "handlers": [
        dict(
            format="{time:%Y-%m-%d at %H:%M:%S} [{level}] {file.name} -> {function}#{line} | {message} ",
            sink="javinfo.log",
            enqueue=True,
            level=20,
        ),
        dict(
            sink=sys.stdout,
            format="<lvl>{level}</lvl>: <y>{module}</y>.<c>{function}#{line}</c> | <lvl>{message}</lvl>",
            enqueue=True,
            colorize=True,
            level=20
        )
    ],
}
logger.configure(**LOGGER_CONFIG)

