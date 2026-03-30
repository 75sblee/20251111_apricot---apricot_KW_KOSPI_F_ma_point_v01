import func.var

import winsound
import numpy as np


from datetime import datetime, time, timedelta

var = func.var.Var


class Lib:
    @staticmethod
    def w_sound(hz, time_ss, cnt):
        """
        self.lib.w_sound(hz=200, time_ss=80, cnt=1) 버튼
        self.lib.w_sound(300, 100, 2)
        self.lib.w_sound(700, 100, 1)
        self.lib.w_sound(hz=700, time_ss=100, cnt=2)

        :param hz: 소리의 주파수 헤르츠 37 - 32767 기본 440
        :param time_ss:
        :param cnt:
        :return:
        """
        for po in range(cnt):
            winsound.Beep(frequency=hz, duration=time_ss)

    @staticmethod
    def encoding(idx):
        try:
            idx = idx.encode('latin-1').decode('cp949')
        except Exception as e:
            _ = e
            idx = idx

        return idx
