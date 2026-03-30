import admin.a_main
from func.var_global import *
import pandas as pd
from datetime import datetime, timedelta


class RlAdmin1:
    def __init__(self):
        self.a = admin.a_main.AMain()

        # 포지션 band
        self.band_upper = None
        self.band_lower = None
        self.entry_time = None

        # 진입봉 실시간 TP 스킵용
        self.entry_candle_time = None

        # 최근 period 기준 고가 기억
        self.prev_value_high = None

        # 안전 초기화
        if not hasattr(var, "medosu_gubun_1"):
            var.medosu_gubun_1 = ""
        if not hasattr(var, "vol_get_1"):
            var.vol_get_1 = 0

    # ======================================================
    # 포지션 상태
    # ======================================================
    @staticmethod
    def _pos_state():
        has_pos = var.vol_get_1 > 0
        is_long = has_pos and var.medosu_gubun_1 == "mesu"
        is_short = has_pos and var.medosu_gubun_1 == "medo"
        return has_pos, is_long, is_short

    # ======================================================
    # 봉마감시 라인정보 출력
    # ======================================================
    @staticmethod
    def _print_close_lines(lines, close_price, time_tag):
        close_price = float(close_price)

        log.debug("")
        log.debug(f"[봉마감] time={time_tag} 종가={close_price:.4f}")
        log.debug(f"[포지션] {var.medosu_gubun_1} vol={var.vol_get_1}")

        for i in range(len(lines) - 1):
            up_name, up = lines[i]
            dn_name, dn = lines[i + 1]
            if up >= close_price >= dn:
                log.debug(
                    f"[현재구간] 상단={up_name}({up:.4f}) | 하단={dn_name}({dn:.4f})"
                )
                log.debug("")
                return

        log.debug("[현재구간] 라인 범위 밖")
        log.debug("")

    # ======================================================
    # 주문 / 청산
    # ======================================================
    def enter_long(self, time_c, upper, lower, line_name, line_value):
        self.band_upper = upper
        self.band_lower = lower
        self.entry_time = time_c
        self.entry_candle_time = var.df.iloc[-1]["time"]

        # ✅ 진입 기준라인 저장
        var.entry_line_name = line_name
        var.entry_line_value = float(line_value)

        var.medosu_gubun_1 = "mesu"
        var.vol_get_1 = var.vol_base_1
        var.price_get_1 = 0

        idx = f"🔴  [진입_매수] 기준={line_name}({line_value:.4f})"
        log.info(idx)
        self.a.ui.log_ui_1(text=idx)
        self.a.order(code=var.code_1, medosu_gubun="mesu", vol=var.vol_get_1)

    def enter_short(self, time_c, upper, lower, line_name, line_value):
        self.band_upper = upper
        self.band_lower = lower
        self.entry_time = time_c
        self.entry_candle_time = var.df.iloc[-1]["time"]

        # ✅ 진입 기준라인 저장
        var.entry_line_name = line_name
        var.entry_line_value = float(line_value)

        var.medosu_gubun_1 = "medo"
        var.vol_get_1 = var.vol_base_1
        var.price_get_1 = 0

        idx = f"🔵  [진입_매도] 기준={line_name}({line_value:.4f})"
        log.info(idx)
        self.a.ui.log_ui_1(text=idx)
        self.a.order(code=var.code_1, medosu_gubun="medo", vol=var.vol_get_1)

    def exit_position(self, price, reason, line_name, line_value):
        idx = f"⭕️  [청산] price={price:.4f} 기준={line_name}({line_value:.4f}) reason={reason}"
        log.info(idx)
        self.a.ui.log_ui_1(text=idx)

        if var.medosu_gubun_1 == "mesu":
            self.a.order(code=var.code_1, medosu_gubun="medo", vol=var.vol_get_1)
        elif var.medosu_gubun_1 == "medo":
            self.a.order(code=var.code_1, medosu_gubun="mesu", vol=var.vol_get_1)

        var.medosu_gubun_1 = ""
        var.vol_get_1 = 0

        self.band_upper = None
        self.band_lower = None
        self.entry_time = None
        self.entry_candle_time = None

        # ✅ 진입 기준라인 초기화
        var.entry_line_name = None
        var.entry_line_value = None

    # ======================================================
    # 실시간 TP 기준 라인 찾기 함수
    # ======================================================
    def _get_tp_line(self, lines, is_long, is_short):
        # ⭐ band 기준으로 TP 가능 여부 판단
        if is_long and self.band_upper is None:
            return None
        if is_short and self.band_lower is None:
            return None

        if var.entry_line_name is None:
            return None

        for i, (name, value) in enumerate(lines):
            if name == var.entry_line_name:
                # 롱 → 위 라인
                if is_long and i - 1 >= 0:
                    return lines[i - 1]

                # 숏 → 아래 라인
                if is_short and i + 1 < len(lines):
                    return lines[i + 1]

        return None

    # ======================================================
    # 라인 생성
    # ======================================================
    @staticmethod
    def _build_lines(value_high):
        lines = []

        # ✅ main도 음수일 때만 활성
        line_base = getattr(var, "line_base", 0)
        if line_base < 0:
            lines.append(("main", value_high))

        rpt = getattr(var, "line_rpt", 0)
        if rpt < 0:
            for n in range(1, 51):
                lvl = value_high * (1 + rpt * n / 100)
                if lvl <= 0:
                    break
                lines.append((f"rpt_{n}", lvl))

        line1 = getattr(var, "line_1", 0)
        if line1 < 0:
            lvl = value_high * (1 + line1 / 100)
            if lvl > 0:
                lines.append(("line_1", lvl))

        lines.sort(key=lambda x: x[1], reverse=True)
        return lines

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
    # 메인 로직
    # ======================================================
    def rl_admin_1(self, data):
        price_c = float(data["price_c"])
        time_c = data["time_c"]
        tick = data["tick"]
        update_min = False

        if var.df is None:
            return

        # ==========================
        # 분봉 갱신
        # ==========================
        base_min = datetime.strptime(var.df.iloc[-1]["time"][:12], "%Y%m%d%H%M")
        next_min = base_min + timedelta(minutes=int(var.min_base))

        if next_min.strftime("%H%M") != time_c[:-2]:
            row = var.df.index[-1]
            var.df.loc[row, "price_c"] = price_c
            var.df.loc[row, "price_h"] = max(var.df.loc[row, "price_h"], price_c)
            var.df.loc[row, "price_l"] = min(var.df.loc[row, "price_l"], price_c)
        else:
            update_min = True
            t = next_min.strftime("%Y%m%d%H%M%S")
            var.df = pd.concat([var.df, pd.DataFrame({
                "time": [t],
                "price_o": [price_c],
                "price_h": [price_c],
                "price_l": [price_c],
                "price_c": [price_c]
            })], ignore_index=True)

            log.debug(f'\n{var.df}')

        if len(var.df) < max(3, int(var.period)):
            return

        # ==========================
        # 최근 period 기준 고가 변경 로그
        # ==========================
        recent = var.df.tail(var.period)
        value_high = float(recent["price_h"].max())

        if self.prev_value_high is None or value_high != self.prev_value_high:
            self.prev_value_high = value_high

            idx = recent["price_h"].idxmax()
            high_row = var.df.loc[idx]

            lines_tmp = self._build_lines(value_high)

            log.info("")
            log.info(
                f"[기준선 변경] "
                f"time={high_row['time']} "
                f"H={value_high:.4f}"
            )

            log_lines = []

            if getattr(var, "line_base", 0) <= 0:
                log_lines.append(("main", value_high))

            if getattr(var, "line_1", 0) <= 0:
                for n, v in lines_tmp:
                    if n == "line_1":
                        log_lines.append((n, v))
                        break

            if getattr(var, "line_rpt", 0) <= 0:
                rpt_lines = [
                    (n, v) for n, v in lines_tmp
                    if n.startswith("rpt_")
                ][:5]
                log_lines.extend(rpt_lines)

            msg = "[기준선]"
            for n, v in log_lines:
                msg += f" {n}={v:.4f}"
            log.info(msg)
            log.info("")

        # 라인 (현재 value_high 기준)
        lines = self._build_lines(value_high)

        has_pos, is_long, is_short = self._pos_state()

        # ==========================
        # 실시간 TP
        # ==========================
        if has_pos:
            if var.tp_1 != 0:
                if tick >= var.tp_1:
                    idx = f'✅  TP 청산 | vol_get : {var.vol_get} | tick : {tick}'
                    log.info(idx)
                    self.a.ui.log_ui(text=idx)

                    if var.medosu_gubun_1 == "mesu":
                        self.a.order(code=var.code_1, medosu_gubun="medo", vol=var.vol_get_1)
                    elif var.medosu_gubun_1 == "medo":
                        self.a.order(code=var.code_1, medosu_gubun="mesu", vol=var.vol_get_1)

                    var.medosu_gubun_1 = ""
                    var.vol_get_1 = 0

                    if var.tp_done_1:
                        self.a.ui.start_pb_1.click()
                        idx = f'✅  TP 청산 후 매매종료 | '
                        log.info(idx)
                        self.a.ui.log_ui_1(text=idx)

                    return

        # ==========================
        # 실시간 TP (진입 기준라인의 위/아래 라인 터치)
        # ==========================
        if has_pos and self.entry_candle_time != var.df.iloc[-1]["time"]:
            tp_line = self._get_tp_line(lines, is_long, is_short)

            if tp_line:
                tp_name, tp_value = tp_line

                # 매수 → 위 라인 터치 시 청산
                if is_long and price_c >= tp_value:
                    log.info(f"⭕️  [TP] {tp_name}({tp_value:.4f}) 실시간 터치")
                    self.exit_position(price_c, "TP", tp_name, tp_value)
                    return

                # 매도 → 아래 라인 터치 시 청산
                if is_short and price_c <= tp_value:
                    log.info(f"⭕️  [TP] {tp_name}({tp_value:.4f}) 실시간 터치")
                    self.exit_position(price_c, "TP", tp_name, tp_value)
                    return

        if not update_min:
            return

        # ==========================
        # 봉 마감 처리 (이전 봉)
        # ==========================
        prev = var.df.iloc[-2]
        o = float(prev["price_o"])
        c = float(prev["price_c"])
        self._print_close_lines(lines, c, prev["time"])

        # ==========================
        # ✅ 스위칭: "진입 기준라인"을 종가로 반대로 넘으면
        # (기준선은 항상 최신 값 사용)
        # ==========================
        has_pos, is_long, is_short = self._pos_state()

        if has_pos and var.entry_line_name is not None:
            # 최신 기준선 가격 다시 찾기
            cur_entry_value = None
            for n, v in lines:
                if n == var.entry_line_name:
                    cur_entry_value = v
                    break

            if cur_entry_value is not None:
                bk_upper = self.band_upper
                bk_lower = self.band_lower
                bk_name = var.entry_line_name

                # 롱 → 기준선 아래로 마감
                if is_long and c < cur_entry_value:
                    log.info(
                        f"🔵  [스위칭] 기준선 하향이탈: "
                        f"{bk_name}({cur_entry_value:.4f}) 종가={c:.4f}"
                    )
                    self.exit_position(c, "SWITCH_ENTRY_LINE", bk_name, cur_entry_value)
                    self.enter_short(time_c, bk_upper, bk_lower, bk_name, cur_entry_value)
                    return

                # 숏 → 기준선 위로 마감
                if is_short and c > cur_entry_value:
                    log.info(
                        f"🔴  [스위칭] 기준선 상향돌파: "
                        f"{bk_name}({cur_entry_value:.4f}) 종가={c:.4f}"
                    )
                    self.exit_position(c, "SWITCH_ENTRY_LINE", bk_name, cur_entry_value)
                    self.enter_long(time_c, bk_upper, bk_lower, bk_name, cur_entry_value)
                    return

        # ==========================
        # 신규 진입 – 라인 돌파 (봉 마감 기준)
        # ==========================
        if not has_pos:
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
        # 신규 진입 – 라인 걸침 (이전 봉 기준, 종가 방향)
        # ==========================
        if not has_pos:
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
