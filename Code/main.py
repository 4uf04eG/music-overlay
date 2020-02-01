from sys import exit

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication

from Code import Application

if __name__ == "__main__":
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = Application()
    exit(app.exec_())
