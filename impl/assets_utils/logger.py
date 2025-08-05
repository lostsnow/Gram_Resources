import logging

logs = logging.getLogger("spider")

logging_format = "[%(asctime)s] %(filename)s [func:%(funcName)s()] [line:%(lineno)d] [%(name)s] %(message)s"
logging_handler = logging.StreamHandler()
logging_handler.setFormatter(logging.Formatter(logging_format))

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging_handler],
)

root_logger = logging.getLogger()
root_logger.setLevel(logging.CRITICAL)

logs.setLevel(logging.INFO)
