import logging
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
import os

LOGS="logs" 

# Make sure the logs directory exists
os.makedirs(LOGS, exist_ok=True)

LOGGING_DIRECTORY = os.path.join(LOGS, "app.log")

def setup_logging(name: str)->logging.Logger:
    logger=logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if logger.hasHandlers():
        return logger
    
    handlers=RotatingFileHandler(
        LOGGING_DIRECTORY,
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=5)

    formatter=logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | "
        "%(filename)s:%(lineno)d | %(message)s"
    )
    handlers.setFormatter(formatter)

    logger.addHandler(handlers)
    logger.addHandler(StreamHandler())
    
    return logger

