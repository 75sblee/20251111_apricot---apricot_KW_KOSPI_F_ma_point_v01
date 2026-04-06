
from func.var import Var as v


class CheJan:
    def __init__(self, a):
        self.a = a
        self.lib = a.lib
        self.log = a.log
        self.kiwoom = self.a.kiwoom

        self.kiwoom.OnReceiveChejanData.connect(self.chejan_slot)
        self.log.info(f'체잔 클라스 실행')

    def chejan_slot(self, s_gubun):
        code = self.kiwoom.dynamicCall("GetChejanData(int)", 9001).strip()
        value = self.kiwoom.dynamicCall("GetChejanData(int)", 913)  # 주문상태 접수/확인/체결
        tr_price = self.kiwoom.dynamicCall("GetChejanData(int)", 910)  # 체결가
        tr_vol = self.kiwoom.dynamicCall("GetChejanData(int)", 911)  # 체결량
        tr_Gubun = self.kiwoom.dynamicCall("GetChejanData(int)", 907)  # 매도수구분 1매도 2매수
        tr_Gubun = tr_Gubun.strip()
        tr_Gubun_1 = self.kiwoom.dynamicCall("GetChejanData(int)", 905)  # 주문구분 매수/매도/매수취소/매도취소/매수정정/매도정정
        tr_type = self.kiwoom.dynamicCall("GetChejanData(int)", 906)  # 주문유형 시장가/지정가
        account = self.kiwoom.dynamicCall("GetChejanData(int)", 9201).strip()
        micheCnt = self.kiwoom.dynamicCall("GetChejanData(int)", 902)
        order_price = self.kiwoom.dynamicCall("GetChejanData(int)", 901)

        value = self.lib.encoding(idx=value)
        tr_type = self.lib.encoding(idx=tr_type)

        # log.info(f'acc : {account}')

        if account == v.acc:
            loger = self.log.debug
            # 로그 정보
            loger(f"")
            loger(f"───────────────────")
            loger(f"s_gubun : {s_gubun}")
            loger(f"code : {code}")
            loger(f"value : {value}")
            loger(f"tr_price : {tr_price}")
            loger(f"tr_vol : {tr_vol}")
            loger(f"tr_Gubun(1매도 2매수) : {tr_Gubun}")
            loger(f"tr_Gubun_1 : {tr_Gubun_1}")
            loger(f"tr_type : {tr_type}")
            loger(f"account : {account}")
            loger(f"micheCnt : {micheCnt}")
            loger(f"order_price : {order_price}")
            loger(f"───────────────────")
            loger(f"")

            if v.tr_sta:
                if s_gubun == "0" and value == "체결":

                    # 체결가 반영
                    price_get_sgn = False
                    if v.medosu_gubun == "mesu":
                        if tr_Gubun == "2":
                            price_get_sgn = True
                    elif v.medosu_gubun == "medo":
                        if tr_Gubun == "1":
                            price_get_sgn = True

                    # log.info(f'medosu_gubun : {var.medosu_gubun} | tr_Gubun : {tr_Gubun} / {type(tr_Gubun)} | '
                    #          f'price_get_sgn : {price_get_sgn}')

                    micheCnt = int(micheCnt)

                    if price_get_sgn and micheCnt == 0:
                        v.price_get = float(tr_price)
                        self.log.info(f'📕 체결가 : {v.price_get}')
                        self.a.ui.table_tr(gubun="set", value=None)

                    # 스위칭 주문
                    if v.sgn_medosu and micheCnt == 0:
                        v.sgn_medosu = False
                        self.log.info(f'청산 확인 후 주문')
                        self.a.order(code=v.code, medosu_gubun=v.medosu_gubun, vol=v.vol_base)

            else:
                if s_gubun == "0" and value == "체결":

                    # 체결가 반영
                    price_get_sgn = False
                    if v.medosu_gubun_1 == "mesu":
                        if tr_Gubun == "2":
                            price_get_sgn = True
                    elif v.medosu_gubun_1 == "medo":
                        if tr_Gubun == "1":
                            price_get_sgn = True

                    # log.info(f'medosu_gubun : {var.medosu_gubun} | tr_Gubun : {tr_Gubun} / {type(tr_Gubun)} | '
                    #          f'price_get_sgn : {price_get_sgn}')

                    micheCnt = int(micheCnt)

                    if price_get_sgn and micheCnt == 0:
                        v.price_get_1 = float(tr_price)
                        self.log.info(f'📕 체결가 : {v.price_get_1}')
                        self.a.ui.table_tr_1(gubun="set", value=None)

                    if v.sgn_medosu and micheCnt == 0:
                        v.sgn_medosu = False
                        self.log.info(f'청산 확인 후 주문')
                        self.a.order(code=v.code_1, medosu_gubun=v.medosu_gubun_1, vol=v.vol_base_1)
