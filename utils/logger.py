import logging
import os
from logging.handlers import RotatingFileHandler

def get_logger(name="ai_system"):
    """
    Initializes and returns a logger with rotating file handler and console handler.
    Logs are stored in the 'data/logs' directory.
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent adding duplicate handlers if the logger is already configured
    if not logger.handlers:
        # File handler (rotates after 5MB, keeps 3 backups)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'extraction.log'), 
            maxBytes=5*1024*1024, 
            backupCount=3
        )
        file_handler.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
