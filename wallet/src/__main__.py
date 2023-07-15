import sys
from PyQt5.QtWidgets import QApplication
from forms.main_window import Wallet


if __name__ == '__main__':
    app = QApplication(sys.argv)
    your_first_app = Wallet()
    your_first_app.show()

    sys.exit(app.exec())
