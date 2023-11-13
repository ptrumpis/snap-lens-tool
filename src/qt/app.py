from PyQt5.QtWidgets import QApplication

from .main_widget import MainWidget


class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.mainWidget = MainWidget()

    def run(self):
        self.mainWidget.show()
        return self.exec_()

    def stop(self):
        self.mainWidget.close()
        self.instance().exit()
