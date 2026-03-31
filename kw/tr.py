
from func.var import Var as v

import pandas as pd


class Tr:
    def __init__(self, kiwoom, event_loop, log):
        self.log = log
        self.kiwoom = kiwoom
        self.event_loop = event_loop
        self.kiwoom.OnReceiveTrData.connect(self.trdata_slot)

    def tr_rq_min(self, gubun):
        if gubun == 0:
            code = v.code
        else:
            code = v.code_1
        min_base = v.min_base
        self.log.info(f'구분 : {gubun} | 코드 : {code} | TR요청 | 분봉 : {min_base}')
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시간단위", min_base)
        result = self.kiwoom.dynamicCall("CommRqData(QString, QString, QString, QString)",
                                         f"{code}_{min_base}분봉{gubun}",
                                         "OPT50029",
                                         "0",
                                         "1000"
                                         )

        self.log.info(f"{code}_{min_base}분봉요청 | 결과 : {result}")
        self.event_loop.exec_()

    def trdata_slot(self, s_scr_num, s_qr_nm, s_tr_code, temp):
        _ = s_scr_num, temp
        gubun = s_qr_nm[-1]

        if v.df is None:
            cnt = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", s_tr_code, s_qr_nm)
            data_list = []
            for i in range(cnt):
                price_c = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                  s_tr_code,
                                                  s_qr_nm,
                                                  i,
                                                  "현재가")
                price_c = abs(float(price_c))

                price_o = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                  s_tr_code,
                                                  s_qr_nm,
                                                  i,
                                                  "시가")
                price_o = abs(float(price_o))

                price_l = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                  s_tr_code,
                                                  s_qr_nm,
                                                  i,
                                                  "저가")
                price_l = abs(float(price_l))

                price_h = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                  s_tr_code,
                                                  s_qr_nm,
                                                  i,
                                                  "고가")
                price_h = abs(float(price_h))

                time_data = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)",
                                                    s_tr_code,
                                                    s_qr_nm,
                                                    i,
                                                    "체결시간").strip()

                data_list.append([str(time_data), price_c, price_o, price_l, price_h])

            df = pd.DataFrame(
                data_list, columns=["time", "price_c", "price_o", "price_l", "price_h"])
            df = df.iloc[::-1]  # 판다스 뒤집기
            v.df = df.reset_index(drop=True)
            if gubun == "0":
                v.df["ma_value"] = v.df["price_c"].rolling(window=v.ma, min_periods=1).mean()
            # pd.set_option('display.max_rows', None)
                if v.df["price_c"].iloc[-2] > v.df["ma_value"].iloc[-2]:
                    v.pst_sta = "mesu"
                elif v.df["price_c"].iloc[-2] < v.df["ma_value"].iloc[-2]:
                    v.pst_sta = "medo"
                self.log.info(f'pst_sta : {v.pst_sta}')
            self.log.info(f'\n{v.df}')

        self.event_loop.exit()
