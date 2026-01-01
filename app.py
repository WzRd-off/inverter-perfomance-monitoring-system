import sys
from app.ui.login_window import LoginWindow
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow

app = QApplication(sys.argv)
window = LoginWindow()



window.show()
app.exec()