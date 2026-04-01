"""
➖➕⁉️❌⭕️️♦️🔒🔍📕📘📁📈📉⌚⏰🚩⭐⚡❤️💥💤💟🅰️🅱️🆑❌❗❓‼️⁉️🔅⚠️❎✅ ➡️ ‍⬅️
🆗🆖🆙#️⃣*️⃣0️⃣1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣🔟▶️⏸️⏯️⏹️⏺️◀️🔼🔽⬆️⬇️➡️⬅️↪️↩️ℹ️☑️✔️➕➖🔴🔵⚪
⬜️◻️◽▫️🔶🔸🔷🔹🔲🔳🕗

"""


import socket
import pandas as pd


class Var:
    my_ip = socket.gethostbyname(socket.gethostname())
    if my_ip == "61.79.25.244":
        user = 1
        print("개발자 접속")
        # acc = "7029535631"  # 모의
        # # my_info_acc_pwd: str = "0000"
        # my_info_id: str = "upend21"
        # my_info_id_pwd: str = "tjdqo082"
        # my_info_cfc: str = ""

        acc = ""
        my_info_id: str = ""
        my_info_id_pwd: str = ""
        my_info_cfc: str = ""
    else:
        user = 2
        print("사용자 접속")
        acc = ""
        my_info_id: str = ""
        my_info_id_pwd: str = ""
        my_info_cfc: str = ""

    code = ""
    code_1 = ""
    step: int = 0
    tr_sta = False    # 프로그램 시작/중지
    tr_sta_1 = False  # 프로그램 시작/중지
    price_c = 0
    price_c_1 = 0
    price_get = 0
    price_get_1 = 0
    df: pd.DataFrame
    vol_get = 0
    vol_get_1 = 0
    vol_base = 0
    vol_base_1 = 0
    time_get = ""    # 진입봉시간
    time_get_1 = ""  # 진입봉시간
    medosu_gubun = ""
    medosu_gubun_1 = ""

    tp = 0
    tp_done = False    # TP 후 매매종료
    tp_1 = 0
    tp_done_1 = False  # TP 후 매매종료

    min_base = ""
    min_base_1 = ""
    chk_time = True
    chk_time_1 = True
    sgn_medosu = False
    sgn_medosu_1 = False
    ma = 0

    period = 0
    line_base = 0
    line_1 = 0
    line_rpt = 0

    sgn_user_buy = False
    sgn_user_buy_1 = False
    pst_sta = ""    # 현재 이평 위치 / 매수자리냐 매도자리냐 / 강제진입에서 "강제" 부분에 대한 정의
    od_fst = False  # 최초 진입 체크 > 최초 1회 자동진입시에만 위치 매매 > 이후는 이평 크로스매매

    clear_cnt_base = 0  # 청산회수 설정
    clear_cnt = 0       # 청산회수
    clear_info = {}     # target_tick / vol
    buy_cdt = False     # 조건진입 체크 상태

    clear_cnt_base_1 = 0  # 청산회수 설정
    clear_cnt_1 = 0       # 청산회수
    clear_info_1 = {}     # target_tick / vol

    entry_line_name = None  # 진입 기준라인 저장 (스위칭용)
    entry_line_value = None
