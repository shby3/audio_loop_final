from PySide6.QtGui import QIcon
from .button_classes import ButtonWrapper, BaseButton
from .button_data import AllButtonsDict
from PySide6.QtCore import QSize

"""
+++------------------------------------------------------------------------+++
This file contains functions that are used to create, manipulate, and implement
buttons and their associated actions.
+++------------------------------------------------------------------------+++
"""

# defines public modules for importing between directories
__all__ = ["make_base_button", "make_buttons_list"]

"""
Constants representing height/width dimensions passed to QSize for icon
resizing. Unit of measure is device-independent pixels.
Doc:
https://doc.qt.io/qtforpython-6/PySide6/QtCore/QSize.html#PySide6.QtCore.QSize
"""
BUTTON_WIDTH = 32
BUTTON_HEIGHT = 32


def make_base_button(button_info: dict):
    """
    Description:
        - Takes a dictionary containing a button's info and uses it to
          create a deployable BaseButton object wrapped in a ButtonWrapper.
    Args:
        - button_info (dict): Stores button info.
                              Keys: "key", "icon", "tooltip", "action",
                                    "button", "shortcut", "handler"
    Returns:
        - wrapper (ButtonWrapper): A deployable button contained in a QWidget.
    Relationship(s):
        - Calls the BaseButton and ButtonWrapper custom classes to create the
          button, which are subclasses of QToolButton and QWidget respectively.
        - Called from make_button_list() to create a list of button objects.
    """
    wrapper = ButtonWrapper()
    button = BaseButton(wrapper)
    button.setCheckable(True)
    button.setIcon(QIcon(button_info["icon"]))
    button.setToolTip(button_info["tooltip"])
    button.clicked.connect(button_info["handler"])
    button.setIconSize(QSize(BUTTON_WIDTH, BUTTON_HEIGHT))
    wrapper.show()
    button_name = button_info["key"]
    # store button object in original reference dictionary for later use
    AllButtonsDict[button_name]["button"] = button
    return wrapper


def make_buttons_list(buttons_dict: dict):
    """
    Description: Takes a reference dictionary containing pointers to a group
                 of buttons' standalone dictionaries and returns a list of
                 button objects.
    Args:
        - buttons_dict (dict): A nested reference dictionary containing
                               pointers to separate button dictionaries.
                               Keys: button name, Values: button dictionary
    Returns:
        - buttons_list (list): A list of deployable BaseButton objects.
    Relationship(s):
        - Calls make_base_button() to create BaseButton objects.
    """
    buttons_list = []  # stores button objects
    for ___, button_dict in buttons_dict.items():
        button = make_base_button(button_dict)
        buttons_list.append(button)
    return buttons_list
