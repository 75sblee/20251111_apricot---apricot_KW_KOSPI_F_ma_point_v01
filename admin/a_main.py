
import ui.ui_main
import kw.logIn
import kw.rl
import kw.tr
import kw.chejan
import kw.order

from admin.a_rl import RlAdmin
from admin.a_rl_1 import RlAdmin1
from ui.ui_main import UiMain
from func.var import Var as v
from func.lib import Lib
from func.db_admin import DbAdmin
from func.log import get_logger

import copy
import sys
import time

from multiprocessing import Queue
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from datetime import datetime, timedelta


class AMain:
    # noinspection PyArgumentList
    def __init__(self):
        # noinspection PyArgumentList,PyCompatibility
        super().__init__()

        self.lib = Lib()
        self.db_admin = DbAdmin()
        self.log = get_logger()

        self.log.info("")
        self.log.info("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
        self.log.info("apricot_KW_KOSPI_F_ma_point_v01_20260330")
        self.log.info("20260330-14")
        self.log.info("■■■■■■■■■■■■■■■■■■■■■■■■■■■■■")
        self.log.info("")

        self.db_admin.get_my_info()

        # ─────────────────── 기본 변수 설정
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.OnReceiveMsg.connect(self.msg_slot)
        self.event_loop = QEventLoop()
        self.ui = UiMain()

        self._rl_admin = RlAdmin()
        self._rl_admin_1 = RlAdmin1()

        self._bar_cnt = 0
        self._bar_cnr_rl = 0
        self._bar_cnr_rl_1 = 0
        self._time_cnt = 0

        self.timer_1 = QTimer()

        self.rl = None
        self.tr = None
        self.chejan = None
        self._rl_admin = None
        self._rl_admin_1 = None

    # ------------------------------------------
    # 주기 실행 타이머 초기화
    # ------------------------------------------
    def init_timers(self):
        # 1초 타이머
        self.timer_1.timeout.connect(self.run_1sec)
        self.timer_1.start(200)

    def on_real_data(self, data):
        price_c = data["price_c"]

        if v.tr_sta:
            v.price_c = price_c

            self.ui.price_c_lb.setText(f'{price_c:.2f}')
            # 프로그레스바
            self.ui.rl_bar.setValue(self._bar_cnr_rl)
            self._bar_cnr_rl += 1
            if self._bar_cnr_rl > 100:
                self._bar_cnr_rl = 0

            self._rl_admin.rl_admin(data)

        if v.tr_sta_1 or v.vol_get_1 != 0:
            v.price_c_1 = price_c

        tick = 0
        if v.vol_get_1 != 0:
            self.ui.price_c_lb_1.setText(f'{price_c:.2f}')
            # 프로그레스바
            self.ui.rl_bar_1.setValue(self._bar_cnr_rl_1)
            self._bar_cnr_rl_1 += 1
            if self._bar_cnr_rl_1 > 100:
                self._bar_cnr_rl_1 = 0

            if v.medosu_gubun_1 == "mesu":
                tick = int((price_c - v.price_get_1) / 0.05)
            elif v.medosu_gubun_1 == "medo":
                tick = int((v.price_get_1 - price_c) / 0.05)

            self.ui.table_tr_1(gubun="rl", value=tick)

        if v.tr_sta_1:
            data["tick"] = tick
            self._rl_admin_1.rl_admin_1(data)

    def run_1sec(self):

        if v.step == 0:
            v.step = 1

            kw.logIn.LogIn(self.kiwoom, self.event_loop)  # 로그인
            self.code_list()

            self.rl = kw.rl.Rl(self.kiwoom)
            self.rl.data_signal.connect(self.on_real_data)
            self.tr = kw.tr.Tr(self.kiwoom, self.event_loop)
            self.chejan = kw.chejan.CheJan()

            self.ui.show()

            self.ui.log_ui(text="프로그램 시작")
            self.ui.log_ui_1(text="프로그램 시작")

            v.step = 2

        elif v.step == 2:
            self.ui.bar_pgr.setValue(self._bar_cnt)
            self._bar_cnt += 1
            if self._bar_cnt > 100:
                self._bar_cnt = 0

        if (v.tr_sta or v.tr_sta_1) and v.df is not None:

            time_now = datetime.now()
            time_value = int(time_now.strftime("%H%M%S"))
            time_idx = time_now.strftime("%H:%M %S")
            self.ui.time_lb.setText(time_idx)
            self.ui.time_lb_1.setText(time_idx)

            if v.tr_sta:
                base_min = v.df['time'].iloc[-1]  # 20251111133500 이런 형태 / 문자열
                base_min = datetime.strptime(base_min, "%Y%m%d%H%M%S")

                chk_time = base_min + timedelta(minutes=int(v.min_base)) - timedelta(seconds=1)

                if 153455 > time_value >= 84550:  # 최소 시작 시간 보장
                    # 1초 전 트리거
                    if time_now >= chk_time:
                        if self._time_cnt == 0:
                            # print("")
                            # log.info(f'')
                            # log.info(f'chk_time : {var.chk_time}')
                            # log.info(f'\n{var.df.iloc[-1]}')
                            if v.chk_time:
                                v.chk_time = False
                                self._time_cnt = 1
                                self.order_run()
                    else:
                        self._time_cnt = 0

                if time_value >= 153455:  # 154455
                    if v.vol_get != 0:
                        self.log.info(f'❌  시간청산')
                        if v.medosu_gubun == "mesu":
                            medosu_gubun = "medo"
                        else:
                            medosu_gubun = "mesu"
                        idx = f'❌  시간청산({v.medosu_gubun}) | 진입개수 : {v.vol_get}'
                        self.log.info(idx)
                        self.ui.log_ui(text=idx)
                        self.order(code=v.code, medosu_gubun=medosu_gubun, vol=v.vol_get)
                        v.vol_get = 0
                    idx = f'⚠️  매매중지 실행'
                    self.log.info(idx)
                    self.ui.log_ui(text=idx)
                    self.ui.start_pb.click()

            if v.vol_get_1 != 0:
                if time_value >= 153455:  # 154455

                    self.log.info(f'❌  시간청산')
                    if v.medosu_gubun_1 == "mesu":
                        medosu_gubun = "medo"
                    else:
                        medosu_gubun = "mesu"
                    idx = f'❌  시간청산({v.medosu_gubun_1}) | 진입개수 : {v.vol_get_1}'
                    self.log.info(idx)
                    self.ui.log_ui_1(text=idx)
                    self.order(code=v.code_1, medosu_gubun=medosu_gubun, vol=v.vol_get_1)
                    v.vol_get_1 = 0
                    idx = f'⚠️  매매중지 실행'
                    self.log.info(idx)
                    self.ui.log_ui_1(text=idx)
                    self.ui.start_pb_1.click()

    def order_run(self):
        # if var.user == 1:
        #     lib.w_sound(700, 100, 1)
        price_c = v.df["price_c"].iloc[-1]
        price_o = v.df["price_o"].iloc[-1]
        price_h = v.df["price_h"].iloc[-1]
        price_l = v.df["price_l"].iloc[-1]
        ma_value = v.df["ma_value"].iloc[-1]
        self.log.info(
            f'medosu_gubun : {v.medosu_gubun} | price_o : {price_o} | price_c : {price_c} | ma_value : {ma_value}')

        price_c_1 = v.df["price_c"].iloc[-2]
        # price_o_1 = var.df["price_o"].iloc[-2]
        ma_value_1 = v.df["ma_value"].iloc[-2]

        if not v.sgn_user_buy:         # 강제 진입이 아닌경우

            if v.vol_get == 0:
                buy_cdt = False
                if not v.od_fst:       # 최초 진입
                    if not v.buy_cdt:  # 조건 진입이 아닐 때
                        chk_buy = False
                        if price_c > ma_value:
                            v.medosu_gubun = "mesu"
                            chk_buy = True

                        elif price_c < ma_value:
                            v.medosu_gubun = "medo"
                            chk_buy = True

                        if chk_buy:
                            # ---------------------
                            # 최초진입
                            # ---------------------
                            v.vol_get = v.vol_base
                            v.clear_cnt = 0
                            idx = f'⭕️  최초진입({v.medosu_gubun}) | 진입개수 : {v.vol_base}'
                            self.log.info(idx)
                            self.ui.log_ui(text=idx)
                            self.order(code=v.code, medosu_gubun=v.medosu_gubun, vol=v.vol_base)

                    else:                 # 조건 진입일 때
                        buy_cdt = True

                else:  # 최초진입이 아닐 때
                    buy_cdt = True

                if buy_cdt:
                    chk_buy = False
                    idx = None
                    if price_c > ma_value and price_c_1 <= ma_value_1:  # 매수 크로스
                        v.medosu_gubun = "mesu"
                        chk_buy = True
                        idx = "크로스진입"
                    elif price_c < ma_value and price_c_1 >= ma_value_1:  # 매도 크로스
                        v.medosu_gubun = "medo"
                        chk_buy = True
                        idx = "크로스진입"
                    elif price_l < ma_value < price_c:  # 이평 터치 후 매수
                        v.medosu_gubun = "mesu"
                        chk_buy = True
                        idx = "이평 터치 후 매수진입"
                    elif price_h > ma_value > price_c:  # 이평 터치 후 매도
                        v.medosu_gubun = "medo"
                        chk_buy = True
                        idx = "이평 터치 후 매도진입"

                    if chk_buy:
                        # ---------------------
                        # 크로스 및 터치 진입
                        # ---------------------
                        v.vol_get = v.vol_base
                        v.clear_cnt = 0
                        idx = f'⭕️  {idx}({v.medosu_gubun}) | 진입개수 : {v.vol_base}'
                        self.log.info(idx)
                        self.ui.log_ui(text=idx)
                        self.order(code=v.code, medosu_gubun=v.medosu_gubun, vol=v.vol_base)

            else:
                if v.medosu_gubun == "mesu":
                    if price_c < ma_value:
                        # ---------------------
                        # 스위칭 매수 > 매도
                        # ---------------------
                        idx = f'⭕️  스위칭(매수 > 매도) | 진입개수 : {v.vol_base}'
                        self.log.info(idx)
                        self.ui.log_ui(text=idx)
                        v.medosu_gubun = "medo"
                        v.clear_cnt = 0
                        v.price_get = 0
                        v.sgn_medosu = True
                        self.order(code=v.code, medosu_gubun=v.medosu_gubun, vol=v.vol_get)
                elif v.medosu_gubun == "medo":
                    if price_c > ma_value:
                        # ---------------------
                        # 스위칭 매수 > 매수
                        # ---------------------
                        idx = f'⭕️  스위칭(매도 > 매수) | 진입개수 : {v.vol_base}'
                        self.log.info(idx)
                        self.ui.log_ui(text=idx)
                        v.medosu_gubun = "mesu"
                        v.clear_cnt = 0
                        v.price_get = 0
                        v.sgn_medosu = True
                        self.order(code=v.code, medosu_gubun=v.medosu_gubun, vol=v.vol_get)

    def code_list(self):
        month_list = self.kiwoom.dynamicCall("GetFutureList()")
        lst = month_list.split(';')
        code_list = [""]
        for i in lst:
            if i[-3:] == "000":
                code_list.append(i)
        code_list.sort()
        self.ui.code_cb.addItems(code_list)
        self.ui.code_cb_1.addItems(code_list)

    def order(self, code, medosu_gubun, vol):
        kw.order.order(self, code=code, medosu_gubun=medosu_gubun, vol=vol)
        # log.info(f'보유수향 : {var.vol_get}')
        if code == v.code:
            self.ui.table_tr(gubun="set", value=None)
        else:
            self.ui.table_tr_1(gubun="set", value=None)

    def pgr_run(self, gubun):
        self.tr.tr_rq_min(gubun)
        # # 실시간 안들어오면 요청
        # if var.user == 2:
        #     self.rl.rl_rq()

    def msg_slot(self, scr_no, rq_nm, code, msg):
        rq_nm = self.lib.encoding(idx=rq_nm)
        msg = self.lib.encoding(idx=msg)
        code_nm = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", [code])
        index = f"스크린: {scr_no}, 요청이름: {rq_nm}, tr: {code_nm}({code}) --- {msg}"
        self.log.info("메세지 슬롯 ************************")
        self.log.info(index)
