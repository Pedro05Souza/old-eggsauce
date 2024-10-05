from colorlog import ColoredFormatter
import logging

__all__ = ['setup_logging', 'bot_logger']

def setup_logging() -> logging.Logger:
        """
        Setup the logging for the bot.

        Returns:
            logging.Logger
        """
        logger = logging.getLogger('bot_logger')
        logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)-8s%(reset)s - %(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "purple",
            },
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger

bot_logger = setup_logging()