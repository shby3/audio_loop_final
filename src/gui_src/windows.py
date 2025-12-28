from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from .button_functions import make_buttons_list
from .button_data import AllButtonsDict, Toolbars
from .toolbars import make_toolbar

"""
+++------------------------------------------------------------------------+++
This file contains classes and functions that are used to create,
manipulate, and implement windows and their associated actions.
+++------------------------------------------------------------------------+++
"""

# defines public modules for importing between directories
__all__ = ["MainWindow"]


class MainWindow(QMainWindow):
    """
    Description:
        - Represents the main window of the application.
    Args:
        - controller (object): the Controller object to use with the GUI.
    Methods:
        - add_buttons():  Adds buttons to the main window layout.
        - add_menu_bar(): Adds actions to the app's  main menu bar.
        - add_toolbars(): Adds a series of toolbars to the main window
                          layout.
        - add_toolbar(buttons, position): Initializes a toolbar with the
                                          desired buttons at the given
                                          position.

    Relationship(s):
        - Called from main()
    """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Audio Looper v1.0")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)
        self.add_menu_bar()
        self.add_toolbars()

    def add_buttons(self):
        """
        Description: Initializes and adds buttons to the window.
        Args:
            - None.
        Returns:
            - None.
        Relationship(s):
            - Uses the info from AllButtonsDict to create buttons.
        """
        buttons = make_buttons_list(AllButtonsDict.copy(), self.controller)
        for button in buttons:
            self.layout.addWidget(button)

    def add_menu_bar(self):
        """
        Description:
            - Initializes and adds entries to the menu bar for the app.
        Args:
            - None.
        Returns:
            - None.
        Relationship(s):
            - None.
        """
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction("Export")

    def add_toolbars(self):
        """
        Description:
            - Initializes and adds entries to the menu bar for the app.
        Args:
            - None.
        Returns:
            - None.
        Relationship(s):
            - Calls make_toolbar(name, button_info)
        """
        for toolbar_name, toolbar_dict, toolbar_position, bar_break in Toolbars:
            self.add_toolbar(toolbar_name, toolbar_dict, toolbar_position, bar_break)

    def add_toolbar(self, name: str, buttons: dict, position: str = "top", bar_break: str = False):
        """
        Description: Adds a toolbar to the main app window at the given
                     position.
        Args:
            - name (str): name of toolbar to display on label.
            - buttons (dict): contains params needed for button creation.
            - position (str): indicates location on main window where
                              toolbar should be positioned.
                              Valid entries: "top", "bottom", "left",
                              "right"

        Returns:
            - None.
        Relationship(s):
            - Calls make_toolbar() function for toolbar initialization.
            - position param is remapped to a value corresponding to the Qt
              property Qt.TopToolBarArea, Qt.BottomToolBarArea,
              Qt.LeftToolBarArea, or Qt.RightToolBarArea.
        """
        valid_positions = {
            "top": Qt.TopToolBarArea,
            "bottom": Qt.BottomToolBarArea,
            "left": Qt.LeftToolBarArea,
            "right": Qt.RightToolBarArea,
        }  # abstracted valid position params for brevity

        #  error checking for invalid position param
        if position not in valid_positions:
            print(f"Invalid toolbar position entered: {position}.")
        else:
            position = valid_positions[position]

        toolbar = make_toolbar(name, buttons, self.controller)
        toolbar.setMinimumSize(64, 32)  # prevents icon cut-off
        self.addToolBar(position, toolbar)

        if bar_break:
            self.addToolBarBreak(Qt.TopToolBarArea)
