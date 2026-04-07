import logging


RESET = "\x1b[0m"
LEVEL_COLORS = {
    logging.DEBUG: "\x1b[36m",
    logging.INFO: "\x1b[32m",
    logging.WARNING: "\x1b[33m",
    logging.ERROR: "\x1b[31m",
    logging.CRITICAL: "\x1b[35m",
}


class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        original_levelname = record.levelname
        color = LEVEL_COLORS.get(record.levelno, "")
        if color:
            record.levelname = f"{color}{original_levelname}{RESET}"
        try:
            return super().format(record)
        finally:
            record.levelname = original_levelname


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(
        ColorFormatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def log_lines(logger: logging.Logger, level: int, message: str) -> None:
    for line in str(message).splitlines() or [""]:
        logger.log(level, line)
