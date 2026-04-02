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

        if self.prev_value_high is None or value_high != self.prev_value_high:

            self.prev_value_high = value_high

            line_dict = dict(lines)

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

            text = f'➡️  기준고가 : {value_high}'
            self.log.info(text)
            self.ui.log_ui_1(text=text)

            self.ui.table_monitoring("line", "line_main", f'{line_main:.2f}' if line_main else "-")
            self.ui.table_monitoring("line", "line_line_1", f'{line_line_1:.2f}' if line_line_1 else "-")
            self.ui.table_monitoring("line", "line_rpt_1", f'{line_rpt_1:.2f}' if line_rpt_1 else "-")

        # ==========================
        # 실시간 TP
        # ==========================
        if has_pos:
            if v.tp_1 != 0:
                if tick >= v.tp_1:
                    idx = f'✅  TP 청산 | vol_get : {v.vol_get_1} | tick : {tick}'
                    self.log.info(idx)
                    self.a.ui.log_ui_1(text=idx)

                    if v.medosu_gubun_1 == "mesu":
                        self.a.order(code=v.code_1, medosu_gubun="medo", vol=v.vol_get_1)
                    elif v.medosu_gubun_1 == "medo":
                        self.a.order(code=v.code_1, medosu_gubun="mesu", vol=v.vol_get_1)

                    v.medosu_gubun_1 = ""
                    v.vol_get_1 = 0
                    v.clear_cnt_1 = 0

                    if v.tp_done_1:
                        self.a.ui.start_pb_1.click()
                        idx = f'✅  TP 청산 후 매매종료 | '
                        self.log.info(idx)
                        self.a.ui.log_ui_1(text=idx)

                    return

        # ==========================
        # 실시간 TP (다음 선 터치)
        # ==========================
        if has_pos and self.entry_candle_time != v.df.iloc[-1]["time"]:

            tp_line = self._get_tp_line(lines, is_long, is_short)

            if tp_line:
                tp_name, tp_value = tp_line

                # 🔴 매수 → 위 라인 도달
                if is_long and price_c >= tp_value:
                    self.log.info(f"⭕️  [TP_line] {tp_name}({tp_value:.4f}) 터치")
                    self.exit_position(price_c, "TP_LINE", tp_name, tp_value)
                    return

                # 🔵 매도 → 아래 라인 도달
                if is_short and price_c <= tp_value:
                    self.log.info(f"⭕️  [TP_line] {tp_name}({tp_value:.4f}) 터치")
                    self.exit_position(price_c, "TP_LINE", tp_name, tp_value)
                    return

        # =========================
        # 분할청산
        # =========================
        if v.vol_get_1 != 0:

            if v.medosu_gubun_1 == "mesu":
                medosu_gubun = "medo"
            else:
                medosu_gubun = "mesu"

            if v.clear_cnt_base_1 != 0:
                chk_clear_cnt = v.clear_cnt_1 + 1

                if v.clear_cnt_base_1 >= chk_clear_cnt:
                    tick_chk = v.clear_info_1[str(chk_clear_cnt)]["target_tick"]
                    vol = v.clear_info_1[str(chk_clear_cnt)]["vol"]

                    if tick >= tick_chk:
                        v.clear_cnt_1 += 1

                        msg = f'✅ {chk_clear_cnt}차 청산 | 남은수량={v.vol_get_1} | 청산={vol}'
                        self.log.info(msg)
                        self.ui.log_ui_1(text=msg)

                        v.vol_get_1 -= vol

                        self.a.order(
                            code=v.code_1,
                            medosu_gubun=medosu_gubun,
                            vol=vol
                        )

        if not update_min:
            return

        # ==========================
        # 봉 마감 처리 (이전 봉)
        # ==========================
        prev = v.df.iloc[-2]
        o = float(prev["price_o"])
        c = float(prev["price_c"])
        self._print_close_lines(lines, c, prev["time"])

        # ==========================
        # ✅ 스위칭: "진입 기준라인"을 종가로 반대로 넘으면
        # (기준선은 항상 최신 값 사용)
        # ==========================
        has_pos, is_long, is_short = self._pos_state()

        if has_pos and v.entry_line_name is not None:
            # 최신 기준선 가격 다시 찾기
            cur_entry_value = None
            for n, v1 in lines:
                if n == v.entry_line_name:
                    cur_entry_value = v1
                    break

            if cur_entry_value is not None:
                bk_upper = self.band_upper
                bk_lower = self.band_lower
                bk_name = v.entry_line_name

                # 롱 → 기준선 아래로 마감
                if is_long and c < cur_entry_value:
                    self.log.info(
                        f"🔵  [스위칭] 기준선 하향이탈: "
                        f"{bk_name}({cur_entry_value:.4f}) 종가={c:.4f}"
                    )
                    self.exit_position(c, "SWITCH_ENTRY_LINE", bk_name, cur_entry_value)
                    self.enter_short(time_c, bk_upper, bk_lower, bk_name, cur_entry_value)
                    return

                # 숏 → 기준선 위로 마감
                if is_short and c > cur_entry_value:
                    self.log.info(
                        f"🔴  [스위칭] 기준선 상향돌파: "
                        f"{bk_name}({cur_entry_value:.4f}) 종가={c:.4f}"
                    )
                    self.exit_position(c, "SWITCH_ENTRY_LINE", bk_name, cur_entry_value)
                    self.enter_long(time_c, bk_upper, bk_lower, bk_name, cur_entry_value)
                    return

        # ==========================
        # 신규 진입 – 라인 돌파 (봉 마감 기준)
        # ==========================
        if not has_pos and self.exit_candle_time != v.df.iloc[-1]["time"]:
            band = self._find_band_with_name(o, lines)
            if band:
                up_name, up, dn_name, dn = band

                if c > up:
                    # 롱 진입 기준라인 = up
                    self.enter_long(time_c, up, dn, up_name, up)
                    return

                if c < dn:
                    # 숏 진입 기준라인 = dn
                    self.enter_short(time_c, up, dn, dn_name, dn)
                    return

        # ==========================
        # 신규 진입 – 라인 걸침 (이전 봉 기준, 종가 방향) - 회기진입
        # ==========================
        if not has_pos and self.exit_candle_time != v.df.iloc[-1]["time"]:
            prev_h = float(prev["price_h"])
            prev_l = float(prev["price_l"])
            prev_c = float(prev["price_c"])

            crossed = self._find_crossed_line(prev_h, prev_l, lines)
            if crossed:
                line_name, line_value = crossed
                band = self._find_band_with_name(line_value, lines)
                if band:
                    up_name, up, dn_name, dn = band

                    if prev_c > line_value:
                        self.enter_long(time_c, up, dn, line_name, line_value)
                        return

                    if prev_c < line_value:
                        self.enter_short(time_c, up, dn, line_name, line_value)
                        return
