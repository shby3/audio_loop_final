from PySide6.QtWidgets import QApplication
from .gui_src.windows import MainWindow
import sys

"""
+++------------------------------------------------------------------------+++
This file contains the core loop of the application.
+++------------------------------------------------------------------------+++
"""


def main():
    """
    Description: Initializes application.
    Args:
        - None passed. Command line arguments read from sys.argv.
    Returns:
        - Exits with system status code.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
