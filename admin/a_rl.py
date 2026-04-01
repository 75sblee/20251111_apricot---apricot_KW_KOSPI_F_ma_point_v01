
from func.var import Var as v

import pandas as pd

from datetime import datetime, timedelta


class RlAdmin:
    def __init__(self, a):
        self.log = a.log
        self.ui = a.ui
        self.a = a

        self._up_and_dw = ""
        self._sgn_time = ""
        self._tick = 0

    def rl_admin(self, data):
        price_c = data["price_c"]
        time_c = data["time_c"]

        if v.df is not None:
            # 판다스
            base_min = v.df['time'].iloc[-1][:12]
            base_min = datetime.strptime(base_min, "%Y%m%d%H%M")
            min_base = base_min + timedelta(minutes=int(v.min_base))
            min1 = min_base.strftime("%H%M")

            # 실시간 시간에서 15분 단위 체크
            min_rl = time_c[:-2]

            # 분봉갱신
            if min1 != min_rl:
                # 분봉 현재가 갱신
                v.df.loc[v.df.index[-1], 'price_c'] = price_c
                v.df["ma_value"] = v.df["price_c"].rolling(window=v.ma, min_periods=1).mean()
                # 분봉 고가 갱신
                if price_c > v.df.loc[v.df.index[-1], "price_h"]:
                    v.df.loc[v.df.index[-1], "price_h"] = price_c
                # 분봉 저가 갱신
                elif price_c < v.df.loc[v.df.index[-1], "price_l"]:
                    v.df.loc[v.df.index[-1], "price_l"] = price_c

            else:
                v.chk_time = True
                # v.df = v.df.iloc[1:].reset_index(drop=True)
                # noinspection PyUnresolvedReferences
                time_data_df = f"{min_base.strftime('%Y%m%d%H%M%S')}"
                v.df = pd.concat([v.df, pd.DataFrame(
                    {"time": [time_data_df], "price_c": [price_c], "price_o": [price_c], "price_l": [price_c],
                     "price_h": [price_c]})],
                                            ignore_index=True)
                v.df["ma_value"] = v.df["price_c"].rolling(window=v.ma, min_periods=1).mean()
                self.log.debug(f'\n{v.df}')

                if v.df["price_c"].iloc[-2] > v.df["ma_value"].iloc[-2]:
                    v.pst_sta = "mesu"
                elif v.df["price_c"].iloc[-2] < v.df["ma_value"].iloc[-2]:
                    v.pst_sta = "medo"
                self.log.debug(f'pst_sta : {v.pst_sta}')
                self.log.debug(f'강제진입여부 : {v.sgn_user_buy}')
                self.log.debug(f'현재보유수량 : {v.vol_get}')

            ma_value_rl = v.df["ma_value"].iloc[-1]
            self.a.ui.table_monitoring(gubun="ma", type_vlaue="ma_value", value=f'{ma_value_rl:.2f}')
            ma_value_1 = v.df["ma_value"].iloc[-2]
            self.a.ui.table_monitoring(gubun="ma", type_vlaue="ma_value_1", value=f'{ma_value_1:.2f}')
            price_c_1 = v.df["price_c"].iloc[-2]
            self.a.ui.table_monitoring(gubun="ma", type_vlaue="price_c_1", value=f'{price_c_1:.2f}')

            if v.vol_get != 0:
                tick = None
                if v.price_get != 0:
                    if v.medosu_gubun == "mesu":
                        tick = int((price_c - v.price_get) / 0.05)
                        medosu_gubun = "medo"
                    elif v.medosu_gubun == "medo":
                        tick = int((v.price_get - price_c) / 0.05)
                        medosu_gubun = "mesu"
                    if tick is not None:
                        self.ui.table_tr(gubun="rl", value=tick)

                        if v.clear_cnt_base != 0:  # 분할 청산이 있을 때
                            chk_clear_cnt = v.clear_cnt + 1
    
                            if v.clear_cnt_base >= chk_clear_cnt:
                                tick_chk = v.clear_info[str(chk_clear_cnt)]["target_tick"]
                                vol = v.clear_info[str(chk_clear_cnt)]["vol"]
                                if tick >= tick_chk:
                                    v.clear_cnt += 1
                                    idx = f'✅  {chk_clear_cnt}차 청산 | vol_get : {v.vol_get} | vol : {vol}'
                                    self.log.info(idx)
                                    self.ui.log_ui(text=idx)
                                    v.vol_get -= vol
                                    self.a.order(code=v.code, medosu_gubun=medosu_gubun, vol=vol)

                        if v.tp != 0:
                            if tick >= v.tp:
                                idx = (f'✅  TP 청산 | vol_get : {v.vol_get} | '
                                       f'다음 진입은 스위칭(혹은 이평 터치) 후 진입이 됩니다.')
                                self.log.info(idx)
                                self.ui.log_ui(text=idx)
                                self.a.order(code=v.code, medosu_gubun=medosu_gubun, vol=v.vol_get)
                                v.vol_get = 0

                                if v.tp_done:
                                    self.ui.start_pb.click()
                                    idx = f'✅  TP 청산 후 매매종료 | '
                                    self.log.info(idx)
                                    self.ui.log_ui(text=idx)
