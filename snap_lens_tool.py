import sys

from src.qt.app import App

if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.run())
