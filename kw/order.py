
from func.var import Var as v


def order(self, code, medosu_gubun, vol):
    """
   주문 결과 반환 값
   -201 	: 주문과부하
   -203 	: 종목코드 미존재
   -300 	: 주문입력값 오류
   -301 	: 계좌비밀번호를 입력하십시오.
   -302 	: 타인 계좌를 사용할 수 없습니다.
   -303 	: 경고-주문수량 200개 초과
   -304 	: 제한-주문수량 400개 초과
   """

    self.lib.w_sound(700, 100, 2)

    self.log.info(f"주문 클래스 | code : {code} | gubun : {medosu_gubun} | vol : {vol}")

    if code is not None:
        # 주문구분
        if medosu_gubun == "mesu":
            rq_name = "신규매수"
            nOrderType = "2"  # 신규매수
        else:
            rq_name = "신규매도"
            nOrderType = "1"  # 신규매도

        # 수량
        try:
            nQty = str(int(vol))
        except Exception as e:
            _ = e
            self.log.error("수량 오류")
            return

        # 기타매매설정
        sPrice = "0"
        # sStop = "0"
        sHogaGb = "3"  # 시장가
        sOrgOrderNo = ""

        result = self.kiwoom.dynamicCall(
            "SendOrderFO(QString, QString, QString, QString, QString, QString, QString, QString, QString, QString)",
            [
                rq_name,  # 주문명
                "8000",  # 화면번호
                v.acc,  # 계좌
                code,  # 종목코드
                "1",  # 주문종류 1:신규매매, 2:정정, 3:취소
                nOrderType,  # 매매구분 1: 매도, 2:매수
                sHogaGb,  # 거래구분 시장가2 지정가1 등등
                nQty,  # 수량 (문자열!)
                sPrice,  # 가격
                sOrgOrderNo  # 원주문번호
            ],
        )

        self.log.info(f"주문 결과 : {result} | {type(result)}")
