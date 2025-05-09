"""A simple script to demonstrate PySide6."""

import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QLabel, QWidget


def main() -> int:
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Simple")
    # icon located in current directory is copied to "share" folder when frozen
    # (see setup.py)
    icon_dir = os.path.join(
        os.path.join(sys.prefix, "share")
        if getattr(sys, "frozen", False)
        else os.path.dirname(__file__)
    )
    icon = QIcon(os.path.join(icon_dir, "logo.svg"))
    window.setWindowIcon(icon)
    window.setGeometry(300, 300, 300, 300)
    label = QLabel(window)
    label.setText("Hello World!")
    label.setGeometry(0, 0, 300, 300)
    label.setAlignment(Qt.AlignCenter)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
