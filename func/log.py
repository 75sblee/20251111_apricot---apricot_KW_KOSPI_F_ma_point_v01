import logging
import os
from datetime import datetime, timedelta


class InfoOnlyFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.INFO


class DebugOnlyFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.DEBUG


class LevelTagFilter(logging.Filter):
    def __init__(self, tag):
        super().__init__()
        self.tag = tag

    def filter(self, record):
        return getattr(record, 'tag', None) == self.tag


# 로그 폴더 생성
if not os.path.exists("log"):
    os.makedirs("log")


def get_logger(name="__main__"):
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger  # 이미 초기화된 경우

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    today = datetime.now().strftime("%Y%m%d")

    # === Formatter (고정폭으로 정렬)
    formatter = logging.Formatter(
        "%(asctime)s [%(filename)-17s:%(funcName)-17s:%(lineno)4d]  %(message)s"
    )

    # === 기본 핸들러: INFO, DEBUG, 콘솔
    fh_info = logging.FileHandler(f"log/INFO_{today}.log", encoding="utf-8")
    fh_info.setLevel(logging.INFO)
    fh_info.addFilter(InfoOnlyFilter())
    fh_info.setFormatter(formatter)

    fh_debug = logging.FileHandler(f"log/DEBUG_{today}.log", encoding="utf-8")
    fh_debug.setLevel(logging.DEBUG)
    fh_debug.addFilter(DebugOnlyFilter())
    fh_debug.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    logger.addHandler(fh_info)
    logger.addHandler(fh_debug)
    logger.addHandler(console)

    # # === info1 ~ info9 / debug1 ~ debug9 핸들러 및 메서드 동적 등록
    # for i in range(1, 10):
    #     # infoX 핸들러
    #     fh_info_x = logging.FileHandler(f"log/INFO_{i}_{today}.log", encoding="utf-8")
    #     fh_info_x.setLevel(logging.INFO)
    #     fh_info_x.addFilter(LevelTagFilter(f"info{i}"))
    #     fh_info_x.setFormatter(formatter)
    #     logger.addHandler(fh_info_x)
    #
    #     # debugX 핸들러
    #     fh_debug_x = logging.FileHandler(f"log/DEBUG_{i}_{today}.log", encoding="utf-8")
    #     fh_debug_x.setLevel(logging.DEBUG)
    #     fh_debug_x.addFilter(LevelTagFilter(f"debug{i}"))
    #     fh_debug_x.setFormatter(formatter)
    #     logger.addHandler(fh_debug_x)
    #
    #     # infoX 메서드
    #     def make_info_func(idx):
    #         def _info(msg, *args, **kwargs):
    #             extra = kwargs.pop("extra", {})
    #             extra["tag"] = f"info{idx}"
    #             logger.info(msg, *args, extra=extra, **kwargs)
    #         return _info
    #     setattr(logger, f"info{i}", make_info_func(i))
    #
    #     # debugX 메서드
    #     def make_debug_func(idx):
    #         def _debug(msg, *args, **kwargs):
    #             extra = kwargs.pop("extra", {})
    #             extra["tag"] = f"debug{idx}"
    #             logger.debug(msg, *args, extra=extra, **kwargs)
    #         return _debug
    #     setattr(logger, f"debug{i}", make_debug_func(i))

    suppress_external_logs()
    return logger


def suppress_external_logs():
    # PyQt, ccxt 등 외부 라이브러리 로그 차단
    logging.getLogger("PyQt5.uic.uiparser").setLevel(logging.WARNING)
    logging.getLogger("PyQt5.uic.properties").setLevel(logging.WARNING)
    logging.getLogger("ccxt").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("websocket").setLevel(logging.WARNING)


def del_log():
    if os.path.exists("log"):
        time_now = datetime.now().strftime("%Y%m%d")
        time_now1 = datetime.strptime(time_now, "%Y%m%d")
        time_result = int((time_now1 - timedelta(days=7)).strftime("%Y%m%d"))
        logging.info("로그 체크//삭제")

        for filename in os.listdir("log"):
            try:
                date_str = filename.split("_")[-1].split(".")[0]
                date_num = int(date_str)
                if date_num < time_result:
                    os.remove(f"log/{filename}")
            except Exception:
                continue
