from sys import exit

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication

from MusicOverlay import Application


def run():
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = Application()
    exit(app.exec_())

if __name__ == "__main__":
    run()
