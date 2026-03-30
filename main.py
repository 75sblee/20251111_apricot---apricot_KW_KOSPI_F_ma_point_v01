from admin.a_main import *
from PyQt5.QtWidgets import *

import sys  # from PyQt5.QtWidgets import
# import logging
# import time
# import os
#
# from datetime import datetime, timedelta


if __name__ == "__main__":
    application = QApplication(sys.argv)
    ex = AMain()
    sys.exit(application.exec_())
