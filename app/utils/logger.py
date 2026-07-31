import logging
from datetime import datetime

EMOJI_LEVELS = {
    logging.DEBUG: "🔍",
    logging.INFO: "🟢",
    logging.WARNING: "🟡",
    logging.ERROR: "🔴",
    logging.CRITICAL: "🚨",
}


class EmojiFormatter(logging.Formatter):
    def format(self, record):
        emoji = EMOJI_LEVELS.get(record.levelno, "")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{emoji} {record.levelname} {timestamp} - {record.getMessage()}"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    return logger
