import logging


def setup_custom_logger():
    """
    Sets up a custom logger for Botly.

    The logger will log all messages with level DEBUG and above to the console.
    The log messages will be formatted as follows:
        "%(levelname)s - %(module)s -> %(funcName)s(%(lineno)d) - %(asctime)s - %(message)s"

    Returns:
        The set up logger.
    """
    formatter = logging.Formatter(
        fmt="%(levelname)s - %(module)s -> %(funcName)s(%(lineno)d) - %(asctime)s - %(message)s"
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger("Botly")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


logger = setup_custom_logger()
