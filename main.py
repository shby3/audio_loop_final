from PySide6.QtWidgets import QApplication
from src.gui_src.windows import MainWindow
import sys
from loop import Loop
from track import Track

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
