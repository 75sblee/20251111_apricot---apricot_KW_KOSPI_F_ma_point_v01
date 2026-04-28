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

        self.exit_candle_time = None

        if not hasattr(v, "medosu_gubun_1"):
            v.medosu_gubun_1 = ""
        if not hasattr(v, "vol_get_1"):
            v.vol_get_1 = 0

        self.prev_lines = None  # 상태값

    # ======================================================
    # 위치 판별 함수
    # ======================================================
    @staticmethod
    def _get_close_position(close, lines):
        for name, lvl in lines:
            if close >= lvl:
                return name, "above"
        return None, "below"

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
        v.clear_cnt_1 = 0

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
        v.clear_cnt_1 = 0

        msg = f"🔵 [진입_매도] 기준={line_name}({line_value:.4f})"
        self.log.info(msg)
        self.ui.log_ui_1(text=msg)

        self.a.order(code=v.code_1, medosu_gubun="medo", vol=v.vol_get_1)

    def exit_position(self, price, reason, line_name, line_value):
        self.exit_candle_time = v.df.iloc[-1]["time"]

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

        self.ui.table_tr_1(gubun="set", value=None)

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
    # 분할청산
    # ======================================================
    def partial_exit(self, price, reason, target_tick, clear_vol):

        msg = f"🟡 [분할청산] price={price:.4f} tick={target_tick} vol={clear_vol} reason={reason}"
        self.log.info(msg)
        self.ui.log_ui_1(text=msg)

        # 현재 포지션 방향 반대로 청산
        if v.medosu_gubun_1 == "mesu":
            self.a.order(code=v.code_1, medosu_gubun="medo", vol=clear_vol)
        elif v.medosu_gubun_1 == "medo":
            self.a.order(code=v.code_1, medosu_gubun="mesu", vol=clear_vol)

        # 수량 감소
        v.vol_get_1 -= clear_vol
        v.clear_cnt_1 += 1

        # 안전장치
        if v.vol_get_1 <= 0:
            v.vol_get_1 = 0
            v.medosu_gubun_1 = ""

        self.ui.table_tr_1(gubun="set", value=None)

    # ======================================================
    # 분할 완료 여부
    # ======================================================
    @staticmethod
    def _is_clear_done():
        if v.clear_cnt_base_1 == 0:
            return True
        return v.clear_cnt_1 >= v.clear_cnt_base_1

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

        # =========================
        # 분봉 업데이트
        # =========================
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

        # =========================
        # 기준 고가 / 라인
        # =========================
        recent = v.df.tail(v.period)
        value_high = float(recent["price_h"].max())
        lines = self._build_lines(value_high)

        has_pos, is_long, is_short = self._pos_state()

        # =========================
        # 기준선 변경 로그
        # =========================
        if self.prev_value_high is None or value_high != self.prev_value_high:

            self.prev_value_high = value_high

            line_dict = dict(lines)
            msg = "[기준선]"
            line_main = ""
            line_line_1 = ""
            line_rpt_1 = ""
            if line_dict.get("main"):
                line_main = f"{line_dict['main']:.2f}"
                msg += f" main={line_main}"
            if line_dict.get("line_1"):
                line_line_1 = f"{line_dict['line_1']:.2f}"
                msg += f" line_1={line_line_1}"
            if line_dict.get("rpt_1"):
                line_rpt_1 = f"{line_dict['rpt_1']:.2f}"
                msg += f" rpt_1={line_rpt_1}"

            self.log.info(msg)
            self.a.ui.table_monitoring(gubun="line", type_vlaue="line_main", value=f'{line_main}')
            self.a.ui.table_monitoring(gubun="line", type_vlaue="line_line_1", value=f'{line_line_1}')
            self.a.ui.table_monitoring(gubun="line", type_vlaue="line_rpt_1", value=f'{line_rpt_1}')

        # =========================
        # 분할청산 (실시간)
        # =========================
        if has_pos and v.clear_cnt_base_1 != 0:

            if v.clear_cnt_1 < v.clear_cnt_base_1:

                clear_key = str(v.clear_cnt_1 + 1)
                clear_data = v.clear_info_1.get(clear_key)

                if clear_data:
                    target_tick = clear_data.get("target_tick", 0)
                    clear_vol = clear_data.get("vol", 0)

                    if target_tick > 0 and clear_vol > 0:

                        if tick >= target_tick:

                            clear_vol = min(clear_vol, v.vol_get_1)

                            self.partial_exit(price_c, "PARTIAL_TP", target_tick, clear_vol)

                            # 🔥 마지막 분할이면 return 안함 (다음 로직 허용)
                            if not self._is_clear_done():
                                return

        # =========================
        # 실시간 TP
        # =========================
        if has_pos and v.tp_1 != 0:

            # 🔥 분할 끝나야 TP 허용
            if self._is_clear_done():

                if tick >= v.tp_1:
                    self.exit_position(price_c, "TP", "", 0)
                    return

        # =========================
        # 실시간 TP (라인)
        # =========================
        if has_pos and self.entry_candle_time != v.df.iloc[-1]["time"]:

            # 🔥 분할 끝나야 허용
            if self._is_clear_done():

                tp_line = self._get_tp_line(lines, is_long, is_short)
                if tp_line:
                    tp_name, tp_value = tp_line

                    if is_long and price_c >= tp_value:
                        self.exit_position(price_c, "TP_LINE", tp_name, tp_value)
                        return

                    if is_short and price_c <= tp_value:
                        self.exit_position(price_c, "TP_LINE", tp_name, tp_value)
                        return

        if not update_min:
            return

        # =========================
        # 봉 마감 정기 로그
        # =========================
        self.log.debug(f'---------------------------------------------')
        self.log.debug(f'has_pos : {has_pos}')
        self.log.debug(f'prev_lines : {self.prev_lines}')
        self.log.debug(f'lines : {lines}')
        self.log.debug(f'entry_line_name : {v.entry_line_name}')
        self.log.debug(f'df : \n{v.df}')

        # =========================
        # 봉 마감 기준
        # =========================
        prev = v.df.iloc[-2]
        o = float(prev["price_o"])
        c = float(prev["price_c"])

        # =========================
        # 🔥 라인 이동 진입
        # =========================
        if (
                self.prev_lines is not None
                and self.prev_lines != lines
        ):

            prev_name, prev_pos = self._get_close_position(c, self.prev_lines)
            curr_name, curr_pos = self._get_close_position(c, lines)

            if curr_name is not None:

                line_value = dict(lines)[curr_name]
                band = self._find_band_with_name(line_value, lines)

                if band:
                    up_name, up, dn_name, dn = band

                    # ---------------------
                    # 🔴 아래 → 위
                    # ---------------------
                    if prev_pos == "below" and curr_pos == "above":

                        if not has_pos:
                            self.enter_long(time_c, up, dn, curr_name, line_value)
                            return

                        if has_pos and is_short:
                            self.exit_position(c, "SWITCH_LINE_MOVE", curr_name, line_value)
                            self.enter_long(time_c, up, dn, curr_name, line_value)
                            return

                    # ---------------------
                    # 🔵 위 → 아래
                    # ---------------------
                    if prev_pos == "above" and curr_pos == "below":

                        if not has_pos:
                            self.enter_short(time_c, up, dn, curr_name, line_value)
                            return

                        if has_pos and is_long:
                            self.exit_position(c, "SWITCH_LINE_MOVE", curr_name, line_value)
                            self.enter_short(time_c, up, dn, curr_name, line_value)
                            return

        # =========================
        # 🔥 캔들 몸통 돌파 진입 (핵심 추가)
        # =========================
        if True:

            for line_name, line_value in lines:

                # ---------------------
                # 🔴 상향 돌파 (시가 아래 → 종가 위)
                # ---------------------
                if o < line_value < c:

                    band = self._find_band_with_name(line_value, lines)
                    if not band:
                        continue

                    up_name, up, dn_name, dn = band

                    if not has_pos:
                        self.enter_long(time_c, up, dn, line_name, line_value)
                        return

                    if has_pos and is_short:
                        self.exit_position(c, "SWITCH_BREAK", line_name, line_value)
                        self.enter_long(time_c, up, dn, line_name, line_value)
                        return

                # ---------------------
                # 🔵 하향 돌파 (시가 위 → 종가 아래)
                # ---------------------
                if o > line_value > c:

                    band = self._find_band_with_name(line_value, lines)
                    if not band:
                        continue

                    up_name, up, dn_name, dn = band

                    if not has_pos:
                        self.enter_short(time_c, up, dn, line_name, line_value)
                        return

                    if has_pos and is_long:
                        self.exit_position(c, "SWITCH_BREAK", line_name, line_value)
                        self.enter_short(time_c, up, dn, line_name, line_value)
                        return

        # =========================
        # 스위칭
        # =========================
        if has_pos and v.entry_line_name is not None:

            cur_entry_value = None
            for n, v1 in lines:
                if n == v.entry_line_name:
                    cur_entry_value = v1
                    break

            if cur_entry_value is not None:

                if is_long and c < cur_entry_value:
                    bk_name = v.entry_line_name

                    self.exit_position(c, "SWITCH", bk_name, cur_entry_value)
                    self.enter_short(time_c, self.band_upper, self.band_lower, bk_name, cur_entry_value)
                    return

                if is_short and c > cur_entry_value:
                    bk_name = v.entry_line_name

                    self.exit_position(c, "SWITCH", bk_name, cur_entry_value)
                    self.enter_long(time_c, self.band_upper, self.band_lower, bk_name, cur_entry_value)
                    return

        # =========================
        # 회기 진입 + 스위칭
        # =========================
        if True:

            prev_h = float(prev["price_h"])
            prev_l = float(prev["price_l"])
            prev_c = float(prev["price_c"])

            for line_name, line_value in lines:

                # 🔥 돌파 봉이면 회기 스킵
                if o < line_value < c or o > line_value > c:
                    continue

                # ---------------------
                # 1️⃣ 터치 조건 (핵심)
                # ---------------------
                touched = (prev_h >= line_value >= prev_l)

                if not touched:
                    continue

                # ---------------------
                # 밴드 찾기
                # ---------------------
                band = self._find_band_with_name(line_value, lines)
                if not band:
                    continue

                up_name, up, dn_name, dn = band

                # =====================
                # 🔴 롱 회기
                # (아래 → 터치 → 위 복귀)
                # =====================
                if prev_c > line_value:

                    # 무포지션 → 진입
                    if not has_pos:
                        self.enter_long(time_c, up, dn, line_name, line_value)
                        return

                    # 숏 보유 → 스위칭
                    if has_pos and is_short:
                        self.exit_position(prev_c, "SWITCH_REVERSE", line_name, line_value)
                        self.enter_long(time_c, up, dn, line_name, line_value)
                        return

                # =====================
                # 🔵 숏 회기
                # (위 → 터치 → 아래 복귀)
                # =====================
                if prev_c < line_value:

                    # 무포지션 → 진입
                    if not has_pos:
                        self.enter_short(time_c, up, dn, line_name, line_value)
                        return

                    # 롱 보유 → 스위칭
                    if has_pos and is_long:
                        self.exit_position(prev_c, "SWITCH_REVERSE", line_name, line_value)
                        self.enter_short(time_c, up, dn, line_name, line_value)
                        return

        # =========================
        # 마지막 상태 저장
        # =========================
        self.prev_lines = lines.copy()
