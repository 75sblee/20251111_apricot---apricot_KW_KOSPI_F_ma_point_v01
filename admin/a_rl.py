
import admin.a_main

from func.var_global import *

import pandas as pd

from datetime import datetime, timedelta


class RlAdmin:
    def __init__(self):
        self.a = admin.a_main.AMain()
        self._up_and_dw = ""
        self._sgn_time = ""
        self._tick = 0

    def rl_admin(self, data):
        price_c = data["price_c"]
        time_c = data["time_c"]

        if var.df is not None:
            # 판다스
            base_min = var.df['time'].iloc[-1][:12]
            base_min = datetime.strptime(base_min, "%Y%m%d%H%M")
            min_base = base_min + timedelta(minutes=int(var.min_base))
            min1 = min_base.strftime("%H%M")

            # 실시간 시간에서 15분 단위 체크
            min_rl = time_c[:-2]

            # 분봉갱신
            if min1 != min_rl:
                # 분봉 현재가 갱신
                var.df.loc[var.df.index[-1], 'price_c'] = price_c
                var.df["ma_value"] = var.df["price_c"].rolling(window=var.ma, min_periods=1).mean()
                # 분봉 고가 갱신
                if price_c > var.df.loc[var.df.index[-1], "price_h"]:
                    var.df.loc[var.df.index[-1], "price_h"] = price_c
                # 분봉 저가 갱신
                elif price_c < var.df.loc[var.df.index[-1], "price_l"]:
                    var.df.loc[var.df.index[-1], "price_l"] = price_c

            else:
                var.chk_time = True
                # var.df = var.df.iloc[1:].reset_index(drop=True)
                # noinspection PyUnresolvedReferences
                time_data_df = f"{min_base.strftime('%Y%m%d%H%M%S')}"
                var.df = pd.concat([var.df, pd.DataFrame(
                    {"time": [time_data_df], "price_c": [price_c], "price_o": [price_c], "price_l": [price_c],
                     "price_h": [price_c]})],
                                            ignore_index=True)
                var.df["ma_value"] = var.df["price_c"].rolling(window=var.ma, min_periods=1).mean()
                log.debug(f'\n{var.df}')

                if var.df["price_c"].iloc[-2] > var.df["ma_value"].iloc[-2]:
                    var.pst_sta = "mesu"
                elif var.df["price_c"].iloc[-2] < var.df["ma_value"].iloc[-2]:
                    var.pst_sta = "medo"
                log.debug(f'pst_sta : {var.pst_sta}')
                log.debug(f'강제진입여부 : {var.sgn_user_buy}')
                log.debug(f'현재보유수량 : {var.vol_get}')

            if var.vol_get != 0:
                tick = None
                if var.price_get != 0:
                    if var.medosu_gubun == "mesu":
                        tick = int((price_c - var.price_get) / 0.05)
                        medosu_gubun = "medo"
                    elif var.medosu_gubun == "medo":
                        tick = int((var.price_get - price_c) / 0.05)
                        medosu_gubun = "mesu"
                    if tick is not None:
                        self.a.ui.table_tr(gubun="rl", value=tick)

                        if var.clear_cnt_base != 0:  # 분할 청산이 있을 때
                            chk_clear_cnt = var.clear_cnt + 1
    
                            if var.clear_cnt_base >= chk_clear_cnt:
                                tick_chk = var.clear_info[str(chk_clear_cnt)]["target_tick"]
                                vol = var.clear_info[str(chk_clear_cnt)]["vol"]
                                if tick >= tick_chk:
                                    var.clear_cnt += 1
                                    idx = f'✅  {chk_clear_cnt}차 청산 | vol_get : {var.vol_get} | vol : {vol}'
                                    log.info(idx)
                                    self.a.ui.log_ui(text=idx)
                                    var.vol_get -= vol
                                    self.a.order(code=var.code, medosu_gubun=medosu_gubun, vol=vol)

                        if var.tp != 0:
                            if tick >= var.tp:
                                idx = (f'✅  TP 청산 | vol_get : {var.vol_get} | '
                                       f'다음 진입은 스위칭(혹은 이평 터치) 후 진입이 됩니다.')
                                log.info(idx)
                                self.a.ui.log_ui(text=idx)
                                self.a.order(code=var.code, medosu_gubun=medosu_gubun, vol=var.vol_get)
                                var.vol_get = 0

                                if var.tp_done:
                                    self.a.ui.start_pb.click()
                                    idx = f'✅  TP 청산 후 매매종료 | '
                                    log.info(idx)
                                    self.a.ui.log_ui(text=idx)
