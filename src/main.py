from PySide6.QtWidgets import QApplication, QInputDialog, QLineEdit
from gui_src.windows import MainWindow
from classes.controller import Controller
from gui_src.file_dialog import ProjectChoiceDialog
import os
import sys

PROJECT_PATH = "../projects/loops"

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
                # Get the name of the project with QInputDialog
                text, ok_pressed = QInputDialog.getText(
                    None,  # Parent widget (None for no parent)
                    "Project namer",  # Dialog title
                    "Enter your project name:",  # Label text
                    QLineEdit.Normal,  # Echo mode (e.g., Normal, NoEcho, Password)
                    ""  # Default text (empty string here)
                )
                if ok_pressed and text != '':
                    print("User entered:", text)
                controller.create_new_loop(name=text)
        elif dialog.choice == ProjectChoiceDialog.OPEN_PROJECT:
            print("User opened:", dialog.project_path)
            controller.load_loop_from_file(dialog.project_path)
    else:
        print("User cancelled")
        sys.exit(0)

    window = MainWindow(controller)
    window.show()
    app.exec()

    # Serialize the Loop upon exiting
    controller.serialize_loop()


if __name__ == "__main__":
    main()
