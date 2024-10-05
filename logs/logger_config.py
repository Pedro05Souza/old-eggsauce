from logs.bot_logger import bot_logger

__all__ = ['set_bot_logger_flag', 'log_info', 'log_warning', 'log_error', 'log_critical']

bot_logger_flag = False

def set_bot_logger_flag(flag: bool) -> None:
    """
    Sets the bot logger flag.

    Args:
        flag (bool): The flag to set.

    Returns:
        None
    """
    global bot_logger_flag
    bot_logger_flag = flag

def log_info(message: str) -> None:
    """
    Logs an info message.

    Args:
        message (str): The message to log.

    Returns:
        None
    """
    if bot_logger_flag:
        bot_logger.info(message)

def log_warning(message: str) -> None:
    """
    Logs a warning message.

    Args:
        message (str): The message to log.

    Returns:
        None
    """
    if bot_logger_flag:
        bot_logger.warning(message)

def log_error(message: str, error: Exception) -> None:
    """
    Logs an error message.

    Args:
        message (str): The message to log.

    Returns:
        None
    """
    if bot_logger_flag:
        bot_logger.error(message, error)

def log_critical(message: str, error: Exception) -> None:
    """
    Logs a critical message.

    Args:
        message (str): The message to log.

    Returns:
        None
    """
    if bot_logger_flag:
        bot_logger.critical(message, error)