
from func.var import Var as v
from func.msg_box import msg_box

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from datetime import datetime


class UiMain(QMainWindow):
    def __init__(self, a, lib, db_admin, log):
        # noinspection PyArgumentList
        super().__init__()
        ui_path = "ui/qt/main.ui"
        uic.loadUi(ui_path, self)

        self.a = a
        self.lib = lib
        self.db_admin = db_admin
        self.log = log

        self.click_to()

        # 테이블수정금지
        self.set_table_non_editable(self.table_tw)
        self.set_table_non_editable(self.table_tw_1)

        time3 = [""]
        for i in range(1, 15):
            value = i * 3
            time3.append(str(value))
        self.buy_cnt_cb.addItems(time3)
        self.buy_cnt_cb_1.addItems(time3)

        self.clear_table_tw_1.horizontalHeader().setVisible(True)  # 기준선매매 분할청산 테이블 해더 보이기

    # 테이블 수정 불가 설정 함수
    @staticmethod
    def set_table_non_editable(*tables):
        for table in tables:
            table.setEditTriggers(QTableWidget.NoEditTriggers)

    def click_to(self):
        # 매매시작
        self.start_pb.clicked.connect(self.start_pb_clicked)
        self.start_pb_1.clicked.connect(self.start_pb_1_clicked)
        # 강제매수
        self.mesu_pb.clicked.connect(self.mesu_pb_clicked)
        self.mesu_pb_1.clicked.connect(self.mesu_pb_1_clicked)
        # 강제매도
        self.medo_pb.clicked.connect(self.medo_pb_clicked)
        self.medo_pb_1.clicked.connect(self.medo_pb_1_clicked)
        # 강제스위칭
        self.switching_pb.clicked.connect(self.switching_pb_clicked)
        self.switching_pb_1.clicked.connect(self.switching_pb_1_clicked)
        # 강제청산
        self.clear_pb.clicked.connect(self.clear_pb_clicked)
        self.clear_pb_1.clicked.connect(self.clear_pb_1_clicked)

        # 청산회수
        self.clear_cnt_cb.currentTextChanged.connect(self.clear_cnt_cb_clicked)
        self.clear_cnt_cb_1.currentTextChanged.connect(self.clear_cnt_cb_1_clicked)
        # 청산테이블변경
        self.clear_table_tw.cellChanged.connect(self.clear_table_on_cell_changed)
        self.clear_table_tw_1.cellChanged.connect(self.clear_table_1_on_cell_changed)

    def start_pb_clicked(self):
        self.lib.w_sound(hz=200, time_ss=80, cnt=1)
        code = self.code_cb.currentText()
        vol_base = self.buy_cnt_cb.currentText()
        min_base = self.min_cb.currentText()
        ma = self.ma_le.text()
        tp = self.tp_le.text()
        v.tp_done = False
        if self.checkBox.isChecked():
            v.tp_done = True
        if code != "" and vol_base != "" and min_base != "" and ma != "":
            if not v.tr_sta:
                # noinspection PyTypeChecker
                v.df = None  # 초기화
                v.code = code
                v.vol_base = int(vol_base)
                v.min_base = min_base[:-2]
                try:
                    v.ma = int(ma)
                    if 1 <= v.ma <= 900:
                        pass
                    else:
                        msg_box(f'이평값은 1~900 사이 값만 가능합니다.')
                        return
                except Exception as e:
                    _ = e
                    msg_box(f'이평값 확인 하세요')
                    return

                if self.buy_cdt_ckb.isChecked():
                    v.buy_cdt = True
                else:
                    v.buy_cdt = False

                idx = f'매매시작정보(이평매매) | 코드 : {code}'
                self.log.info(idx)
                self.log_ui(text=idx)
                idx = f'매매시작정보(이평매매) | 분봉 : {v.min_base}'
                self.log.info(idx)
                self.log_ui(text=idx)
                idx = f'매매시작정보(이평매매) | 이평 : {v.ma}'
                self.log.info(idx)
                self.log_ui(text=idx)
                idx = f'매매시작정보(이평매매) | medosu_gubun : {v.medosu_gubun}'
                self.log.info(idx)
                self.log_ui(text=idx)
                idx = f'매매시작정보(이평매매) | 보유수량 : {v.vol_get}'
                self.log.info(idx)
                self.log_ui(text=idx)
                idx = f'매매시작정보(이평매매) | 조건진입상태 : {v.buy_cdt}'
                self.log.info(idx)
                self.log_ui(text=idx)
                idx = f'매매시작정보(이평매매) | TP : {tp}'
                self.log.info(idx)
                self.log_ui(text=idx)
                idx = f'매매시작정보(이평매매) | tp_sta : {v.tp_done}'
                self.log.info(idx)
                self.log_ui(text=idx)

                self.log.info(f'clear_info : {v.clear_info}')

                if v.clear_info:
                    clear_cnt_sum = 0
                    for i in v.clear_info:
                        vol = v.clear_info[i]["vol"]
                        clear_cnt_sum += vol
                    if clear_cnt_sum > v.vol_base - 1:
                        msg_box(f'분할 청산 개수 확인 하세요')
                        return

                v.tr_sta = True
                idx = "✅ 매매시작"
                self.log.info(idx)
                self.log_ui(text=idx)
                self.start_pb.setText("매매중지")
                self.start_pb_1.setDisabled(True)
                self.code_cb.setDisabled(True)
                self.code_cb_1.setDisabled(True)
                self.buy_cnt_cb.setDisabled(True)
                self.buy_cnt_cb_1.setDisabled(True)
                self.min_cb.setDisabled(True)
                self.min_cb_1.setDisabled(True)
                self.ma_le.setDisabled(True)
                self.clear_cnt_cb.setDisabled(True)

                self.mesu_pb_1.setDisabled(True)
                self.medo_pb_1.setDisabled(True)
                self.switching_pb_1.setDisabled(True)
                self.clear_pb_1.setDisabled(True)

                self.tp_le.setDisabled(True)
                self.checkBox.setDisabled(True)

                # 테이블수정금지
                self.set_table_non_editable(self.clear_table_tw)

                if tp != "":
                    v.tp = int(tp)

                self.a.pgr_run(0)
            else:
                v.tr_sta = False
                idx = "✅ 매매중지"
                self.log.info(idx)
                self.log_ui(text=idx)
                self.start_pb.setText("매매시작")
                self.start_pb_1.setDisabled(False)
                self.min_cb.setDisabled(False)
                self.min_cb_1.setDisabled(False)
                self.ma_le.setDisabled(False)

                self.mesu_pb_1.setDisabled(False)
                self.medo_pb_1.setDisabled(False)
                self.switching_pb_1.setDisabled(False)
                self.clear_pb_1.setDisabled(False)

                self.tp_le.setDisabled(False)
                self.checkBox.setDisabled(False)

                if v.vol_get == 0:
                    self.code_cb.setDisabled(False)
                    self.code_cb_1.setDisabled(False)
                    self.buy_cnt_cb.setDisabled(False)
                    self.buy_cnt_cb_1.setDisabled(False)

                if v.clear_cnt == 0:
                    self.clear_cnt_cb.setDisabled(False)
                    # 테이블수정
                    self.clear_table_tw.setEditTriggers(QAbstractItemView.AllEditTriggers)

        else:
            idx = f'⚠️  입력내용 확인 하세요'
            msg_box(idx)
            self.log.info(idx)
            self.log_ui(text=idx)

    def start_pb_1_clicked(self):
        self.lib.w_sound(hz=200, time_ss=80, cnt=1)
        code = self.code_cb_1.currentText()
        vol_base = self.buy_cnt_cb_1.currentText()
        min_base = self.min_cb_1.currentText()

        period = self.period_le.text()
        line_base = self.line_base_le.text()
        line_1 = self.line_1_le.text()
        line_rpt = self.line_rpt_le.text()

        tp = self.tp_le_2.text()
        if tp != "":
            v.tp_1 = int(tp)
        v.tp_done = False
        if self.checkBox_2.isChecked():
            v.tp_done = True

        if (code != "" and vol_base != "" and min_base != "" and period != "" and line_base != ""
                and line_1 != "" and line_rpt != ""):
            if not v.tr_sta_1:
                # noinspection PyTypeChecker
                v.df = None  # 초기화
                v.code_1 = code
                v.vol_base_1 = int(vol_base)
                v.min_base = min_base[:-2]
                try:
                    v.period = int(period)
                    if 1 <= v.period <= 900:
                        pass
                    else:
                        msg_box(f'기간값은 1~900 사이 값만 가능합니다.')
                        return
                    v.line_base = float(line_base)
                    v.line_1 = float(line_1)
                    v.line_rpt = float(line_rpt)
                except Exception as e:
                    _ = e
                    msg_box(f'입력내용 확인 하세요')
                    return

                idx = f'매매시작정보(기준선매매) | 코드 : {code}'
                self.log.info(idx)
                self.log_ui_1(text=idx)
                idx = f'매매시작정보(기준선매매) | 설정계약수 : {vol_base}'
                self.log.info(idx)
                self.log_ui_1(text=idx)
                idx = f'매매시작정보(기준선매매) | 분봉 : {v.min_base}'
                self.log.info(idx)
                self.log_ui_1(text=idx)
                idx = f'매매시작정보(기준선매매) | medosu_gubun : {v.medosu_gubun_1}'
                self.log.info(idx)
                self.log_ui_1(text=idx)
                idx = f'매매시작정보(기준선매매) | 보유수량 : {v.vol_get_1}'
                self.log.info(idx)
                self.log_ui_1(text=idx)
                idx = f'매매시작정보(기준선매매) | 기간 : {v.period}'
                self.log.info(idx)
                self.log_ui_1(text=idx)
                idx = f'매매시작정보(기준선매매) | 메인기준선 : {v.line_base}'
                self.log.info(idx)
                self.log_ui_1(text=idx)
                idx = f'매매시작정보(기준선매매) | 1차기준선 : {v.line_1}'
                self.log.info(idx)
                self.log_ui_1(text=idx)
                idx = f'매매시작정보(기준선매매) | 연속 기준선 : {v.line_rpt}'
                self.log.info(idx)
                self.log_ui_1(text=idx)

                idx = f'매매시작정보(기준선매매) | TP : {tp}'
                self.log.info(idx)
                self.log_ui_1(text=idx)
                idx = f'매매시작정보(기준선매매) | tp_sta : {v.tp_done_1}'
                self.log.info(idx)
                self.log_ui_1(text=idx)

                idx = f'매매시작정보(기준선매매) | 분할청산회수 : {v.clear_cnt_base_1}'
                self.log.info(idx)
                self.log_ui_1(text=idx)

                self.log.info(f'clear_info : {v.clear_info}')

                if v.clear_info_1:
                    clear_cnt_sum = 0
                    for i in v.clear_info_1:
                        vol = v.clear_info_1[i]["vol"]
                        clear_cnt_sum += vol
                    if clear_cnt_sum > v.vol_base_1 - 1:
                        msg_box(f'분할 청산 개수 확인 하세요')
                        return

                v.tr_sta_1 = True
                idx = "✅ 매매시작"
                self.log.info(idx)
                self.log_ui_1(text=idx)
                self.start_pb_1.setText("매매중지")
                self.start_pb.setDisabled(True)
                self.mesu_pb.setDisabled(True)
                self.medo_pb.setDisabled(True)
                self.switching_pb.setDisabled(True)
                self.clear_pb.setDisabled(True)
                self.ma_le.setDisabled(True)
                self.code_cb_1.setDisabled(True)
                self.code_cb.setDisabled(True)
                self.buy_cnt_cb_1.setDisabled(True)
                self.buy_cnt_cb.setDisabled(True)
                self.min_cb_1.setDisabled(True)
                self.min_cb.setDisabled(True)

                self.period_le.setDisabled(True)
                self.line_base_le.setDisabled(True)
                self.line_1_le.setDisabled(True)
                self.line_rpt_le.setDisabled(True)

                self.mesu_pb.setDisabled(True)
                self.medo_pb.setDisabled(True)
                self.switching_pb.setDisabled(True)
                self.clear_pb.setDisabled(True)

                self.clear_cnt_cb_1.setDisabled(True)
                self.tp_le_2.setDisabled(True)
                self.checkBox_2.setDisabled(True)

                self.buy_cdt_ckb.setDisabled(True)

                self.clear_cnt_cb.setDisabled(True)
                self.clear_table_tw.setDisabled(True)
                self.tp_le.setDisabled(True)
                self.checkBox.setDisabled(True)

                self.clear_table_tw_1.setDisabled(True)

                # noinspection PyProtectedMember
                self.a._rl_admin_1.prev_value_high = None
                self.a.pgr_run(1)
            else:
                v.tr_sta_1 = False
                idx = "✅ 매매중지"
                self.log.info(idx)
                self.log_ui_1(text=idx)
                self.start_pb_1.setText("매매시작")
                self.start_pb.setDisabled(False)
                self.mesu_pb.setDisabled(False)
                self.medo_pb.setDisabled(False)
                self.switching_pb.setDisabled(False)
                self.clear_pb.setDisabled(False)
                self.ma_le.setDisabled(False)
                self.min_cb_1.setDisabled(False)
                self.min_cb.setDisabled(False)

                self.period_le.setDisabled(False)
                self.line_base_le.setDisabled(False)
                self.line_1_le.setDisabled(False)
                self.line_rpt_le.setDisabled(False)

                self.mesu_pb.setDisabled(False)
                self.medo_pb.setDisabled(False)
                self.switching_pb.setDisabled(False)
                self.clear_pb.setDisabled(False)

                self.clear_cnt_cb_1.setDisabled(False)
                self.tp_le_2.setDisabled(False)
                self.checkBox_2.setDisabled(False)

                self.buy_cdt_ckb.setDisabled(False)

                self.clear_cnt_cb.setDisabled(False)
                self.clear_table_tw.setDisabled(False)
                self.tp_le.setDisabled(False)
                self.checkBox.setDisabled(False)

                self.clear_table_tw_1.setDisabled(False)

                if v.vol_get_1 == 0:
                    self.code_cb_1.setDisabled(False)
                    self.code_cb.setDisabled(False)
                    self.buy_cnt_cb_1.setDisabled(False)
                    self.buy_cnt_cb.setDisabled(False)

        else:
            idx = f'⚠️  입력내용 확인 하세요'
            msg_box(idx)
            self.log.info(idx)
            self.log_ui_1(text=idx)

    # 강제매수
    def mesu_pb_clicked(self):
        self.lib.w_sound(hz=200, time_ss=80, cnt=1)
        if v.vol_get == 0:

            # ---------------------
            # 강제매수
            # ---------------------
            v.medosu_gubun = "mesu"
            v.vol_get = v.vol_base
            idx = f'⭕️  강제매수 | 진입개수 : {v.vol_base}'
            self.log.info(idx)
            self.log_ui(text=idx)
            self.a.order(code=v.code, medosu_gubun=v.medosu_gubun, vol=v.vol_base)

            if v.pst_sta == "medo":
                v.sgn_user_buy = True  # 강제매수 시그널
                idx = f'✅  매도자리 강제 매수 진입 > 청산은 사용자가 해야 됩니다.'
                self.log.info(idx)
                self.log_ui(text=idx)

        else:
            msg_box(f'보유중 입니다. 청산 후 사용하세요')

    # 강제매수1
    def mesu_pb_1_clicked(self):
        self.lib.w_sound(hz=200, time_ss=80, cnt=1)

        if v.vol_get_1 != 0:
            msg_box('보유중 입니다. 청산 후 사용하세요')
            return

        if v.code_1 == "":
            v.code_1 = self.code_cb_1.currentText()
            if v.code_1 == "":
                msg_box(f'코드 확인하세요')
                return

        if v.vol_base_1 == 0:
            try:
                v.vol_base_1 = int(self.buy_cnt_cb_1.currentText())
            except Exception as e:
                _ = e
                msg_box("입력내용 확인하세요")
                self.log.info(f'계약수 확인안됨')
                return

        if v.tr_sta_1:
            idx = f'사용자 강제 진입 > 자동매매로직 블로킹 실행 > 매매중지'
            self.log.info(idx)
            self.log_ui_1(text=idx)
            v.tr_sta_1 = False

        # ---------------------
        # 롱 진입
        # ---------------------
        v.medosu_gubun_1 = "mesu"
        v.vol_get_1 = v.vol_base_1

        idx = f'⭕️ 강제매수(롱) 진입 > 청산은 사용자가 해야 됩니다.'

        self.log.info(idx)
        self.log_ui_1(text=idx)

        self.a.order(code=v.code_1, medosu_gubun="mesu", vol=v.vol_base_1)
        if v.price_c_1 == 0:
            self.a.rl.rl_rq(v.code_1)

    # 강제매도
    def medo_pb_clicked(self):
        self.lib.w_sound(hz=200, time_ss=80, cnt=1)
        if v.vol_get == 0:
            # ---------------------
            # 강제매도
            # ---------------------
            v.medosu_gubun = "medo"
            v.vol_get = v.vol_base
            idx = f'⭕️  강제매도 | 진입개수 : {v.vol_base}'
            self.log.info(idx)
            self.log_ui(text=idx)
            self.a.order(code=v.code, medosu_gubun=v.medosu_gubun, vol=v.vol_base)

            if v.pst_sta == "mesu":
                v.sgn_user_buy = True  # 강제매수 시그널
                idx = f'✅  매수자리 강제 매도 진입 > 청산은 사용자가 해야 됩니다.'
                self.log.info(idx)
                self.log_ui(text=idx)
        else:
            msg_box(f'보유중 입니다. 청산 후 사용하세요')

    # 강제매도1
    def medo_pb_1_clicked(self):
        self.lib.w_sound(hz=200, time_ss=80, cnt=1)

        if v.vol_get_1 != 0:
            msg_box('보유중 입니다. 청산 후 사용하세요')
            return

        if v.vol_base_1 == 0:
            try:
                v.vol_base_1 = int(self.buy_cnt_cb_1.currentText())
            except Exception as e:
                _ = e
                msg_box("입력내용 확인하세요")
                self.log.info(f'계약수 확인안됨')
                return

        if v.code_1 == "":
            v.code_1 = self.code_cb_1.currentText()
            if v.code_1 == "":
                msg_box(f'코드 확인하세요')
                return

        if v.tr_sta_1:
            idx = f'사용자 강제 진입 > 자동매매로직 블로킹 실행 > 매매중지'
            self.log.info(idx)
            self.log_ui_1(text=idx)
            v.tr_sta_1 = False

        # ---------------------
        # 숏 진입
        # ---------------------
        v.medosu_gubun_1 = "medo"
        v.vol_get_1 = v.vol_base_1

        idx = f'⭕️ 강제매도(숏) 진입 > 청산은 사용자가 해야 됩니다.'

        self.log.info(idx)
        self.log_ui_1(text=idx)

        self.a.order(code=v.code_1, medosu_gubun="medo", vol=v.vol_base_1)
        if v.price_c_1 == 0:
            self.a.rl.rl_rq(v.code_1)

    # 강제스위칭
    def switching_pb_clicked(self):
        self.lib.w_sound(hz=200, time_ss=80, cnt=1)
        if v.vol_get == 0:
            msg_box(f'스위칭 할 보유수량이 없습니다.')
            # v.sgn_user_buy = True
        else:
            if v.medosu_gubun == "mesu":
                v.medosu_gubun = "medo"
                v.sgn_medosu = True
                v.sgn_user_buy = False
                v.price_get = 0
                v.clear_cnt = 0

                idx = f'⭕️  강제 스위칭(매수 > 매도) | 진입개수 : {v.vol_base}'
                self.log.info(idx)
                self.log_ui(text=idx)
                self.a.order(code=v.code, medosu_gubun=v.medosu_gubun, vol=v.vol_get)

                if v.pst_sta == "mesu":
                    v.sgn_user_buy = True  # 강제매수 시그널
                    idx = f'✅  매수자리 강제 매도 진입 > 청산은 사용자가 해야 됩니다.'
                    self.log.info(idx)
                    self.log_ui(text=idx)

            else:
                v.medosu_gubun = "mesu"
                v.sgn_medosu = True
                v.sgn_user_buy = False
                v.price_get = 0
                v.clear_cnt = 0

                idx = f'⭕️  강제 스위칭(매도 > 매수) | 진입개수 : {v.vol_base}'
                self.log.info(idx)
                self.log_ui(text=idx)
                self.a.order(code=v.code, medosu_gubun=v.medosu_gubun, vol=v.vol_get)

                if v.pst_sta == "medo":
                    v.sgn_user_buy = True  # 강제매수 시그널
                    idx = f'✅  매도자리 강제 매수 진입 > 청산은 사용자가 해야 됩니다.'
                    self.log.info(idx)
                    self.log_ui(text=idx)

    # 강제스위칭1
    def switching_pb_1_clicked(self):
        self.lib.w_sound(hz=200, time_ss=80, cnt=1)
        if v.vol_get_1 == 0:
            msg_box(f'스위칭 할 보유수량이 없습니다.')
            # v.sgn_user_buy = True
        else:
            if v.medosu_gubun_1 == "mesu":
                v.medosu_gubun_1 = "medo"
                v.sgn_medosu = True
                # v.sgn_user_buy = False
                v.price_get_1 = 0

                idx = f'⭕️  강제 스위칭1(매수 > 매도) | 진입개수 : {v.vol_base_1}'
                self.log.info(idx)
                self.log_ui_1(text=idx)
                self.a.order(code=v.code_1, medosu_gubun=v.medosu_gubun_1, vol=v.vol_get_1)

            else:
                v.medosu_gubun_1 = "mesu"
                v.sgn_medosu = True
                # v.sgn_user_buy = False
                v.price_get_1 = 0

                idx = f'⭕️  강제 스위칭1(매도 > 매수) | 진입개수 : {v.vol_base_1}'
                self.log.info(idx)
                self.log_ui_1(text=idx)
                self.a.order(code=v.code_1, medosu_gubun=v.medosu_gubun_1, vol=v.vol_get_1)

    # 강제청산
    def clear_pb_clicked(self):
        self.lib.w_sound(hz=200, time_ss=80, cnt=1)
        if v.vol_get == 0:
            msg_box(f'청산 할 보유수량이 없습니다.')
        else:
            v.sgn_user_buy = False

            if v.medosu_gubun == "mesu":
                medosu_gubun = "medo"
            else:
                medosu_gubun = "mesu"

            idx = f'⭕️  강제청산({medosu_gubun}) | 현재포지션 : {v.medosu_gubun} | 청산개수 : {v.vol_get}'
            self.log.info(idx)
            self.log_ui(text=idx)
            v.price_get = 0
            self.a.order(code=v.code, medosu_gubun=medosu_gubun, vol=v.vol_get)
            v.medosu_gubun = ""
            v.vol_get = 0
            v.clear_cnt = 0

            idx = f'✅  사용자 강제 청산 요청 > 다음 진입은 스위칭(혹은 이평 터치) 후 진입이 됩니다.'
            self.log.info(idx)
            self.log_ui(text=idx)
            self.table_tr(gubun="set", value=0)

    # 강제청산1
    def clear_pb_1_clicked(self):
        self.lib.w_sound(hz=200, time_ss=80, cnt=1)
        if v.vol_get_1 == 0:
            msg_box(f'청산 할 보유수량이 없습니다.')
        else:
            # v.sgn_user_buy = False

            if v.medosu_gubun_1 == "mesu":
                medosu_gubun = "medo"
            else:
                medosu_gubun = "mesu"

            idx = f'⭕️  강제청산1({medosu_gubun}) | 현재포지션 : {v.medosu_gubun_1} | 청산개수 : {v.vol_get_1}'
            self.log.info(idx)
            self.log_ui_1(text=idx)
            v.price_get_1 = 0
            self.a.order(code=v.code_1, medosu_gubun=medosu_gubun, vol=v.vol_get_1)
            v.medosu_gubun_1 = ""
            v.vol_get_1 = 0
            v.price_get_1 = 0

            idx = f'✅  사용자 강제 청산 요청'
            self.log.info(idx)
            self.log_ui_1(text=idx)
            self.table_tr_1(gubun="set", value=0)

            if not v.tr_sta_1:
                idx = f'>> 자동매매 중지 중입니다. 자동매매를 원하실경우 매매시작을 누르세요'
                self.log.info(idx)
                self.log_ui_1(text=idx)

    # 청산회수 이평매매
    def clear_cnt_cb_clicked(self, text):
        # <<< 시그널 막기 시작
        self.clear_table_tw.blockSignals(True)

        self.lib.w_sound(hz=200, time_ss=80, cnt=1)
        self.clear_table_tw.setRowCount(0)
        v.clear_cnt_base = 0  # 초기화
        v.clear_info = {}
        if text != "":
            row = int(text)
            v.clear_cnt_base = row + 1

            self.clear_table_tw.setRowCount(row)

            for i in range(row):
                cnt = i + 1
                self.clear_table_tw.setItem(i, 0, QTableWidgetItem(f"{cnt}차"))
                self.clear_table_tw.item(i, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)

                self.clear_table_tw.setItem(i, 1, QTableWidgetItem(f" "))
                self.clear_table_tw.item(i, 1).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
                self.clear_table_tw.setItem(i, 2, QTableWidgetItem(f" "))
                self.clear_table_tw.item(i, 2).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)

                v.clear_info.setdefault(str(cnt), {"target_tick": 0, "vol": 0})
        # <<< 시그널 다시 켜기
        self.clear_table_tw.blockSignals(False)

    # 청산회수 기준선매매
    def clear_cnt_cb_1_clicked(self, text):
        # <<< 시그널 막기 시작
        self.clear_table_tw_1.blockSignals(True)

        self.lib.w_sound(hz=200, time_ss=80, cnt=1)
        self.clear_table_tw_1.setRowCount(0)
        v.clear_cnt_base_1 = 0  # 초기화
        v.clear_info_1 = {}
        if text != "":
            row = int(text)
            v.clear_cnt_base_1 = row

            self.clear_table_tw_1.setRowCount(row)

            for i in range(row):
                cnt = i + 1
                self.clear_table_tw_1.setItem(i, 0, QTableWidgetItem(f"{cnt}차"))
                self.clear_table_tw_1.item(i, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)

                self.clear_table_tw_1.setItem(i, 1, QTableWidgetItem(f" "))
                self.clear_table_tw_1.item(i, 1).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
                self.clear_table_tw_1.setItem(i, 2, QTableWidgetItem(f" "))
                self.clear_table_tw_1.item(i, 2).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)

                v.clear_info_1.setdefault(str(cnt), {"target_tick": 0, "vol": 0})
        # <<< 시그널 다시 켜기
        self.clear_table_tw_1.blockSignals(False)

    # 청산테이블변경 이평매매
    def clear_table_on_cell_changed(self, row, col):
        try:
            self.lib.w_sound(hz=200, time_ss=80, cnt=1)
            key = str(row + 1)
            data = self.clear_table_tw.item(row, col).text()
            if data == "":
                data = 0
            else:
                data = int(data)

            if col == 1:
                value = "target_tick"
            elif col == 2:
                value = "vol"
            else:
                value = None
            if value is not None:
                v.clear_info[key][value] = data
        except Exception as e:
            _ = e
            msg_box("입력내용 확인 하세요")
        self.log.info(f'clear_info(이평매매 : {v.clear_info}')

    # 청산테이블변경 기준선매매
    def clear_table_1_on_cell_changed(self, row, col):
        try:
            self.lib.w_sound(hz=200, time_ss=80, cnt=1)
            key = str(row + 1)
            data = self.clear_table_tw_1.item(row, col).text()
            if data == "":
                data = 0
            else:
                data = int(data)

            if col == 1:
                value = "target_tick"
            elif col == 2:
                value = "vol"
            else:
                value = None
            if value is not None:
                v.clear_info_1[key][value] = data
        except Exception as e:
            _ = e
            msg_box("입력내용 확인 하세요")
        self.log.info(f'clear_info(기준선매매) : {v.clear_info_1}')

    def table_tr(self, gubun, value):
        table = self.table_tw
        vol_get = v.vol_get
        medosu_gubun = v.medosu_gubun
        price_get = v.price_get
        align = Qt.AlignCenter | Qt.AlignCenter
        if gubun == "set":
            if vol_get == 0:
                table.setItem(0, 1, QTableWidgetItem(f" "))
                table.setItem(1, 1, QTableWidgetItem(f" "))
                table.setItem(2, 1, QTableWidgetItem(f" "))
                table.setItem(3, 1, QTableWidgetItem(f" "))
            else:
                table.setItem(0, 1, QTableWidgetItem(f"{medosu_gubun}"))
                table.item(0, 1).setTextAlignment(align)

                table.setItem(1, 1, QTableWidgetItem(f"{price_get}"))
                table.item(1, 1).setTextAlignment(align)

                table.setItem(2, 1, QTableWidgetItem(f"{vol_get}"))
                table.item(2, 1).setTextAlignment(align)

        elif gubun == "rl":
            table.setItem(3, 1, QTableWidgetItem(f"{value}"))
            table.item(3, 1).setTextAlignment(align)

    def table_tr_1(self, gubun, value):
        table = self.table_tw_1
        vol_get = v.vol_get_1
        medosu_gubun = v.medosu_gubun_1
        price_get = v.price_get_1
        align = Qt.AlignCenter | Qt.AlignCenter
        if gubun == "set":
            if vol_get == 0:
                table.setItem(0, 1, QTableWidgetItem(f" "))
                table.setItem(1, 1, QTableWidgetItem(f" "))
                table.setItem(2, 1, QTableWidgetItem(f" "))
                table.setItem(3, 1, QTableWidgetItem(f" "))
            else:
                table.setItem(0, 1, QTableWidgetItem(f"{medosu_gubun}"))
                table.item(0, 1).setTextAlignment(align)

                table.setItem(1, 1, QTableWidgetItem(f"{price_get}"))
                table.item(1, 1).setTextAlignment(align)

                table.setItem(2, 1, QTableWidgetItem(f"{vol_get}"))
                table.item(2, 1).setTextAlignment(align)

        elif gubun == "rl":
            table.setItem(3, 1, QTableWidgetItem(f"{value}"))
            table.item(3, 1).setTextAlignment(align)

    def table_monitoring(self, gubun, type_vlaue, value):
        table = getattr(self, f'mnt_tw_{gubun}')
        align = Qt.AlignCenter | Qt.AlignCenter
        row = None
        if type_vlaue == "time":
            row = 0
        elif type_vlaue == "price_c":
            row = 1
        elif type_vlaue == "ma_value":
            row = 2
        elif type_vlaue == "ma_value_1":
            row = 3
        elif type_vlaue == "price_c_1":
            row = 4

        elif type_vlaue == "line_main":
            row = 2
        elif type_vlaue == "line_line_1":
            row = 3
        elif type_vlaue == "line_rpt_1":
            row = 4

        if row is not None:
            table.setItem(row, 1, QTableWidgetItem(f"{value}"))
            table.item(row, 1).setTextAlignment(align)

    def log_ui(self, text):
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = f'[{time_now}] {text}'
        self.log_tb.append(text)

    def log_ui_1(self, text):
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = f'[{time_now}] {text}'
        self.log_tb_1.append(text)
