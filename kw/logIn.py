
class LogIn:
    def __init__(self, kiwoom, event_loop, lib, log):

        self.lib = lib
        self.log = log
        self.kiwoom = kiwoom

        self.event_loop = event_loop

        self.kiwoom.OnEventConnect.connect(self.login_slot)
        self.login()

    def login(self):
        self.kiwoom.dynamicCall("CommConnect()")
        self.log.debug("이벤트루프 실행")
        self.event_loop.exec_()

    def login_slot(self, err_code):
        if err_code != 0:
            self.lib.w_sound(700, 100, 2)
            self.log.info("login : False", err_code)
        else:
            index = f"로그인이 되었습니다."
            self.event_loop.exit()
            self.log.debug("이벤트루프 종료")
            self.log.info(index)
