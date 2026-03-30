
from PyQt5.QtWidgets import QMessageBox


def msg_box(text):
    # noinspection PyArgumentList,PyTypeChecker
    QMessageBox.warning(None, '경고', text, QMessageBox.Ok)
