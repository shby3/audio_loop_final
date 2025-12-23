from PySide6.QtWidgets import QToolBar, QLabel
from .button_functions import make_buttons_list

"""
+++------------------------------------------------------------------------+++
This file contains classes and functions that are used to create,
manipulate, and implement toolbars and their associated actions.
+++------------------------------------------------------------------------+++
"""

# defines public modules for importing between directories
__all__ = ["make_toolbar"]


def make_toolbar(name: str, buttons_info: dict):
    """
    Description: Takes a nested dictionary containing entries for a group
                 of buttons' and adds them to a single toolbar.
    Args:
        - name (str): Name of the toolbar
        - buttons_info (dict): stores entries for a group of related buttons
    Returns:
        - toolbar (QToolBar): a deployable toolbar object
    Relationship(s):
        - Called from MainWindow class.
    """
    buttons = make_buttons_list(buttons_info)
    toolbar = QToolBar()
    label = QLabel(name)
    label.setStyleSheet("font-weight: bold; margin-right: 8px;")
    toolbar.addWidget(label)
    for button in buttons:
        toolbar.addWidget(button)

    return toolbar
