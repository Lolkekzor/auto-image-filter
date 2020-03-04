import logging
import structlog
from structlog.stdlib import LoggerFactory


def setup():
    logging.basicConfig(
        format="%(levelname)s - %(message)s",
        filename="log.log",
        filemode="w",
        level=logging.INFO,
    )
    structlog.configure(logger_factory=LoggerFactory())
