from PySide6.QtWidgets import QApplication
from src.gui_src.windows import MainWindow
import sys
from controller import Controller
from src.gui_src.file_dialog import ProjectChoiceDialog
import os
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
    # Controller object creation
    controller = Controller()

    # Directory management
    Controller.create_directories()
    print(f"cwd: {os.getcwd()}")

    # Startup GUI, or exit if cancelled
    app = QApplication(sys.argv)
    dialog = ProjectChoiceDialog()
    if dialog.exec() == ProjectChoiceDialog.Accepted:
        if dialog.choice == ProjectChoiceDialog.NEW_PROJECT:
            print("User chose NEW project")
            controller.loop = Loop()
        elif dialog.choice == ProjectChoiceDialog.OPEN_PROJECT:
            print("User opened:", dialog.project_path)
            controller.load_loop_from_file(dialog.project_path)
    else:
        print("User cancelled")
        sys.exit(0)

    window = MainWindow(controller)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
