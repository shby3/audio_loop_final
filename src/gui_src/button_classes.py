from PySide6.QtWidgets import QWidget, QVBoxLayout, QToolButton
from PySide6.QtCore import Qt

"""
+++------------------------------------------------------------------------+++
This file contains classes that are used to create, manipulate, and implement
buttons and their associated actions.
+++------------------------------------------------------------------------+++
"""

# defines public modules for importing between directories
__all__ = ["BaseButton", "ButtonWrapper"]


class BaseButton(QToolButton):
    """
    Description: Represents an interactive button in the GUI.
    Args:
        - parent (QWidget): the constructor the button belongs to.
    Methods:
        - None.
    Relationship(s):
        - Should be called with an instance of the ButtonWrapper
          QWidget-subclass passed as its parent.
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAutoRaise(True)


class ButtonWrapper(QWidget):
    """
    Description: Wrapper that holds a single GUI Button.

    Args:
        - None.
    Methods:
        - add_button(button): adds a button to the wrapper's layout
    Relationship(s):
        - Should be passed as the parent for any new BaseButton(QToolButton)
          instance.
    """

    def __init__(self):
        super().__init__()
        self.setMinimumSize(70, 32)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def add_button(self, button: QToolButton):
        """
        Description: Adds a button to the wrapper's layout.
        Args:
            - button (QToolButton): button to add to the layout.
        Returns:
            - None.
        Relationship(s):
            - Should be passed an instance of the BaseButton(QtoolButton)
              subclass.
        """
        self.layout.addWidget(button, alignment=Qt.AlignCenter)
