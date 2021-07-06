import logging


# Logging Methods
def log_load_info(path):
    logging.basicConfig(filename=path,
                        level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    return logging


def log_load_debug(path):
    logging.basicConfig(filename=path,
                        level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    return logging


def define_logging(path):
    logger_info = log_load_info(path)
    logger_bug = log_load_debug(path)
    return logger_info,logger_bug