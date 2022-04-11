from logging import getLogger, INFO, Formatter, StreamHandler, FileHandler
import sys


def set_logger(name, today_str, LOG_PATH):
    """ロガーの設定
    input:today_str
    return:logger
    """
    logger = getLogger(name)
    logger.setLevel(INFO)
    ch = StreamHandler(sys.stdout)
    ch.setLevel(INFO)
    ch.setFormatter(Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    fh = FileHandler(f"{LOG_PATH}/log_{today_str}.txt")
    fh.setLevel(INFO)
    fh.setFormatter(Formatter("%(asctime)s - %(name)s - %(levelname)s -%(message)s"))
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger
