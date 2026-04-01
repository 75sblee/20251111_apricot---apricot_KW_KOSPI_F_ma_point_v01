from func.var import Var as v

import pandas as pd
from datetime import datetime, timedelta


class RlAdmin1:
    def __init__(self, a):
        self.log = a.log
        self.ui = a.ui
        self.a = a

        # 포지션 band
        self.band_upper = None
        self.band_lower = None
        self.entry_time = None

        # 진입봉 TP 스킵
        self.entry_candle_time = None

        # 기준 고가 기억
        self.prev_value_high = None

        if not hasattr(v, "medosu_gubun_1"):
            v.medosu_gubun_1 = ""
        if not hasattr(v, "vol_get_1"):
            v.vol_get_1 = 0

    # ======================================================
    # 포지션 상태
    # ======================================================
    @staticmethod
    def _pos_state():
        has_pos = v.vol_get_1 > 0
        is_long = has_pos and v.medosu_gubun_1 == "mesu"
        is_short = has_pos and v.medosu_gubun_1 == "medo"
        return has_pos, is_long, is_short

    # ======================================================
    # 봉마감 라인 출력
    # ======================================================
    def _print_close_lines(self, lines, close_price, time_tag):
        close_price = float(close_price)

        self.log.debug("")
        self.log.debug(f"[봉마감] time={time_tag} 종가={close_price:.4f}")
        self.log.debug(f"[포지션] {v.medosu_gubun_1} vol={v.vol_get_1}")

        for i in range(len(lines) - 1):
            up_name, up = lines[i]
            dn_name, dn = lines[i + 1]
            if up >= close_price >= dn:
                self.log.debug(
                    f"[현재구간] 상단={up_name}({up:.4f}) | 하단={dn_name}({dn:.4f})"
                )
                self.log.debug("")
                return

        self.log.debug("[현재구간] 라인 범위 밖")
        self.log.debug("")

    # ======================================================
    # 주문 / 청산
    # ======================================================
    def enter_long(self, time_c, upper, lower, line_name, line_value):
        self.band_upper = upper
        self.band_lower = lower
        self.entry_time = time_c
        self.entry_candle_time = v.df.iloc[-1]["time"]

        v.entry_line_name = line_name
        v.entry_line_value = float(line_value)

        v.medosu_gubun_1 = "mesu"
        v.vol_get_1 = v.vol_base_1
        v.price_get_1 = 0

        msg = f"🔴 [진입_매수] 기준={line_name}({line_value:.4f})"
        self.log.info(msg)
        self.ui.log_ui_1(text=msg)

        self.a.order(code=v.code_1, medosu_gubun="mesu", vol=v.vol_get_1)

    def enter_short(self, time_c, upper, lower, line_name, line_value):
        self.band_upper = upper
        self.band_lower = lower
        self.entry_time = time_c
        self.entry_candle_time = v.df.iloc[-1]["time"]

        v.entry_line_name = line_name
        v.entry_line_value = float(line_value)

        v.medosu_gubun_1 = "medo"
        v.vol_get_1 = v.vol_base_1
        v.price_get_1 = 0

        msg = f"🔵 [진입_매도] 기준={line_name}({line_value:.4f})"
        self.log.info(msg)
        self.ui.log_ui_1(text=msg)

        self.a.order(code=v.code_1, medosu_gubun="medo", vol=v.vol_get_1)

    def exit_position(self, price, reason, line_name, line_value):
        msg = f"⭕️ [청산] price={price:.4f} 기준={line_name}({line_value:.4f}) reason={reason}"
        self.log.info(msg)
        self.ui.log_ui_1(text=msg)

        if v.medosu_gubun_1 == "mesu":
            self.a.order(code=v.code_1, medosu_gubun="medo", vol=v.vol_get_1)
        elif v.medosu_gubun_1 == "medo":
            self.a.order(code=v.code_1, medosu_gubun="mesu", vol=v.vol_get_1)

        v.medosu_gubun_1 = ""
        v.vol_get_1 = 0

        self.band_upper = None
        self.band_lower = None
        self.entry_time = None
        self.entry_candle_time = None

        v.entry_line_name = None
        v.entry_line_value = None

    # ======================================================
    # TP 기준 라인
    # ======================================================
    def _get_tp_line(self, lines, is_long, is_short):
        if is_long and self.band_upper is None:
            return None
        if is_short and self.band_lower is None:
            return None
        if v.entry_line_name is None:
            return None

        for i, (name, value) in enumerate(lines):
            if name == v.entry_line_name:
                if is_long and i - 1 >= 0:
                    return lines[i - 1]
                if is_short and i + 1 < len(lines):
                    return lines[i + 1]
        return None

    # ======================================================
    # 라인 생성 (완전 수정)
    # ======================================================
    @staticmethod
    def _build_lines(value_high):
        lines = []

        # main (% 기준선)
        if v.line_base != 0:
            lvl = value_high * (1 + v.line_base / 100)
            if lvl > 0:
                lines.append(("main", lvl))

        # rpt
        if v.line_rpt != 0:
            for n in range(1, 51):
                lvl = value_high * (1 + v.line_rpt * n / 100)
                if lvl <= 0:
                    break
                lines.append((f"rpt_{n}", lvl))

        # line_1
        if v.line_1 != 0:
            lvl = value_high * (1 + v.line_1 / 100)
            if lvl > 0:
                lines.append(("line_1", lvl))

        lines.sort(key=lambda x: x[1], reverse=True)
        return lines

    # ======================================================
    # 밴드 찾기
    # ======================================================
    @staticmethod
    def _find_band_with_name(price, lines):
        for i in range(len(lines) - 1):
            up_name, up = lines[i]
            dn_name, dn = lines[i + 1]
            if up >= price >= dn:
                return up_name, up, dn_name, dn
        return None

    @staticmethod
    def _find_crossed_line(prev_h, prev_l, lines):
        for name, lvl in lines:
            if prev_h >= lvl >= prev_l:
                return name, lvl
        return None

    # ======================================================
    # 메인
    # ======================================================
    def rl_admin_1(self, data):

        price_c = float(data["price_c"])
        time_c = data["time_c"]
        tick = data["tick"]
        update_min = False

        if v.df is None:
            return

        # 분봉 업데이트
        base_min = datetime.strptime(v.df.iloc[-1]["time"][:12], "%Y%m%d%H%M")
        next_min = base_min + timedelta(minutes=int(v.min_base))

        if next_min.strftime("%H%M") != time_c[:-2]:
            row = v.df.index[-1]
            v.df.loc[row, "price_c"] = price_c
            v.df.loc[row, "price_h"] = max(v.df.loc[row, "price_h"], price_c)
            v.df.loc[row, "price_l"] = min(v.df.loc[row, "price_l"], price_c)
        else:
            update_min = True
            t = next_min.strftime("%Y%m%d%H%M%S")
            v.df = pd.concat([v.df, pd.DataFrame({
                "time": [t],
                "price_o": [price_c],
                "price_h": [price_c],
                "price_l": [price_c],
                "price_c": [price_c]
            })], ignore_index=True)

        if len(v.df) < max(3, int(v.period)):
            return

        # 기준 고가
        recent = v.df.tail(v.period)
        value_high = float(recent["price_h"].max())

        # 기준선 변경
        if self.prev_value_high is None or value_high != self.prev_value_high:

            self.prev_value_high = value_high

            lines_tmp = self._build_lines(value_high)
            line_dict = dict(lines_tmp)

            line_main = line_dict.get("main")
            line_line_1 = line_dict.get("line_1")
            line_rpt_1 = line_dict.get("rpt_1")

            msg = "[기준선]"
            if line_main:
                msg += f" main={line_main:.4f}"
            if line_line_1:
                msg += f" line_1={line_line_1:.4f}"
            if line_rpt_1:
                msg += f" rpt_1={line_rpt_1:.4f}"

            self.log.info(msg)

            self.a.ui.table_monitoring("line", "line_main", f'{line_main:.2f}' if line_main else "-")
            self.a.ui.table_monitoring("line", "line_line_1", f'{line_line_1:.2f}' if line_line_1 else "-")
            self.a.ui.table_monitoring("line", "line_rpt_1", f'{line_rpt_1:.2f}' if line_rpt_1 else "-")

        lines = self._build_lines(value_high)
        has_pos, is_long, is_short = self._pos_state()

        # 분할청산
        if v.vol_get_1 != 0:  # 물량 보유 중일 때

            if v.medosu_gubun_1 == "mesu":
                medosu_gubun = "medo"
            elif v.medosu_gubun_1 == "medo":
                medosu_gubun = "mesu"

            if v.clear_cnt_base != 0:  # 분할 청산이 있을 때
                chk_clear_cnt = v.clear_cnt + 1

                if v.clear_cnt_base >= chk_clear_cnt:
                    tick_chk = v.clear_info_1[str(chk_clear_cnt)]["target_tick"]
                    vol = v.clear_info_1[str(chk_clear_cnt)]["vol"]
                    if tick >= tick_chk:
                        v.clear_cnt_1 += 1
                        idx = f'✅  {chk_clear_cnt}차 청산 | vol_get : {v.vol_get_1} | vol : {vol}'
                        self.log.info(idx)
                        self.ui.log_ui_1(text=idx)
                        v.vol_get -= vol
                        self.a.order(code=v.code, medosu_gubun=medosu_gubun, vol=vol)
