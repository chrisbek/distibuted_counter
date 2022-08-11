import logging


class LogService:
    @staticmethod
    def get_logger(log_level: str) -> logging.Logger:
        logger = logging.getLogger()
        logger.setLevel(log_level)
        return logger
