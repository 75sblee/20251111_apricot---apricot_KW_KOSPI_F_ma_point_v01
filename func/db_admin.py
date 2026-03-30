import func.var
import func.log

import pickle
# import pymongo

var = func.var.Var
log = func.log.get_logger()


class DbAdmin:
    def __init__(self):
        pass

    @staticmethod
    def get_my_info():
        file_path = "db/my_info.txt"
        with open(file_path, "r", encoding="utf-8") as f:

            data = []
            for line in f:
                line = line.strip()  # 개행 문자 제거
                data.append(line)

            var.acc = data[0].split(":")[1]
            var.my_info_id = data[1].split(":")[1]
            var.my_info_id_pwd = data[2].split(":")[1]
            var.my_info_cfc = data[3].split(":")[1]

            log.info(f'계좌 : {var.acc}')
            log.info(f'아이디 : {var.my_info_id}')
            log.info(f'아이디비번 : {var.my_info_id_pwd}')
            log.info(f'인증서비번 : {var.my_info_cfc}')
