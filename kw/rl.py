
from func.var import Var as v

from datetime import datetime, timedelta
# noinspection PyPackageRequirements
from PyQt5.QtCore import QObject, pyqtSignal


class Rl(QObject):
    data_signal = pyqtSignal(dict)

    def __init__(self, kiwoom, lib, log):
        super().__init__()
        self.lib = lib
        self.log = log
        self.kiwoom = kiwoom
        self.kiwoom.OnReceiveRealData.connect(self.realdata_slot)

    def rl_rq(self, code):
        self.log.info(f'실시간 요청 : {v.code}')
        result = self.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)", "1000", code, "10", "0")
        self.log.info(f'실시간 요청 결과 : {result}')

    def realdata_slot(self, sCode, sRealType):
        """

        :param sCode:
        :param sRealType:
        # :param sRealData:
        :return:
        """
        code = sCode.strip()

        sRealType = self.lib.encoding(sRealType)

        if sRealType == "선물시세":
            price_c = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, 10)  # fid 현재가
            price_c = abs(float(price_c))
            time_c = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, 20)

            data = {
                "price_c": price_c,
                "time_c": time_c,
            }
            # noinspection PyUnresolvedReferences
            self.data_signal.emit(data)
