""" 
The purpose of this code is to mock up how we can use PySide6 in tandem with
our desire for a two-path file structure for loop and track storage. The long-
term goals of this code would be to migrate this into our final code base so
that app.py starts this process - the user starts our application, points to
their home directory and our storage structure is on it's way!

Testing for this can be done in the mock-up GUI (which was made so we can test
the tree structure associated with PyQt and PySide6.)
Written by: Michelle Mann
"""

import sys
from pathlib import Path

from PySide6.QtCore import QDir
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileSystemModel, QTreeView,
    QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout,
    QFileDialog, QMessageBox, QInputDialog, QStatusBar
)

from send2trash import send2trash  # cross-platform Recycle Bin / Trash App


class FileTreeBrowser(QMainWindow):
    """
    Description: Main Window Demo Class. This class will probably not be
    used directly, but it's components can be used in our actual project.

    Args:
        - None.
    Methods:
        _current_path: get current path
        _refresh_parent: updates our parent folder for UI purposes
    Relationship(s):
        - Should be passed as the parent for any new BaseButton(QToolButton)
        instance.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Loop Station - Content List Demo")
        self.resize(900, 600)

        # Store parent folder as starting location
        start_dir = str(Path(__file__).parent)

        # Set parent to starting location
        self.model = QFileSystemModel()
        self.model.setRootPath(start_dir)
        self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)

        # ==== TREE VIEW ====
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(start_dir))
        self.tree.setColumnWidth(0, 320)
        self.tree.setAlternatingRowColors(True)

        self.tree.doubleClicked.connect(self.open_with_default_app)

        sel = self.tree.selectionModel()
        sel.selectionChanged.connect(self.on_selection_changed)

        # ==== CONTROLS ====
        self.choose_btn = QPushButton("Choose Folder…")
        self.choose_btn.clicked.connect(self.create_home_directory)

        self.rename_btn = QPushButton("Rename…")
        self.rename_btn.clicked.connect(self.rename_selected)

        self.trash_btn = QPushButton("Move to Trash")
        self.trash_btn.clicked.connect(self.trash_selected)

        self.selected_label = QLabel("No item selected")

        toolbar = QHBoxLayout()
        toolbar.addWidget(self.choose_btn)
        toolbar.addStretch(1)
        toolbar.addWidget(self.rename_btn)
        toolbar.addWidget(self.trash_btn)

        layout = QVBoxLayout()
        layout.addLayout(toolbar)
        layout.addWidget(QLabel("Current folder tree:"))
        layout.addWidget(self.tree, 1)
        layout.addWidget(QLabel("Selected path:"))
        layout.addWidget(self.selected_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

    # ==== HELPERS ====
    def _current_path(self) -> Path | None:
        """
        Description: Updates current path.
        Args: None
        Returns:
            - Path: The path location
            - None:
        Relationship(s):
            - Helper function used in trash_selected() and rename_selected()
        """
        idxs = self.tree.selectionModel().selectedIndexes()
        if not idxs:
            return None
        return Path(self.model.filePath(idxs[0]))

    # ==== EVENT HANDLERS ====
    def create_home_directory(self):
        """
        Description: Allows user to choose root folder for project.
        Args:
            - None
        Returns:
            - (Indirect) User creates two new directories after home directory
            is selected: "Tracks" and "Loops"
        Relationship(s):
            - None
        """
        folder = QFileDialog.getExistingDirectory(self, "Choose folder",
                                                  str(Path.home()))
        if folder:
            root = Path(folder)

        # Create subfolders: Loops, Tracks
        try:
            loops_dir = root / "Loops"
            tracks_dir = root / "Tracks"
            loops_dir.mkdir(parents=True, exist_ok=True)
            tracks_dir.mkdir(parents=True, exist_ok=True)

            # Update the UI to show the new root
            self.model.setRootPath(str(root))
            self.tree.setRootIndex(self.model.index(str(root)))
            self.selected_label.setText("No item selected")
            self.status.showMessage(f"Set project root: {root}", 2500)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Creating Folders",
                f"Could not create subfolders in:\n{folder}\n\nError: {e}"
            )

    def open_with_default_app(self, index=None):
        """
        Description: "Loads" a file. No, this actually doesn't load things
        -yet- but this is the mechanism by which we'll store the file path and
        initiate a "load" to various UI integrations. For now, we'll print to
        output the file name.
        Args:
            - None
        Returns:
            - (Indirect) User opens file.
        Relationship(s):
            - None
        """
        # Prefer the index passed by the signal; otherwise use the current
        # selection
        if index is None or not index.isValid():
            index = self.tree.selectionModel().currentIndex()
            if not index.isValid():
                QMessageBox.information(self, "Open File",
                                        "Please select a file.")
                return

        index = index.siblingAtColumn(0)

        # No file is selected
        if not index.isValid():
            QMessageBox.information(self, "Open File",
                                    "Please select a file first.")
            return

        # Selected file path
        path = Path(self.model.filePath(index))

        # We don't care about folders out of folder nav. We only care about
        # reading files
        if path.is_dir():
            QMessageBox.information(self, "Open File",
                                    "Attempting to open a folder.")
            return
        else:
            print(f"Loaded file: {path} for use!")

    def on_selection_changed(self, selected, _deselected):
        """
        Description: Updates selection on tree when new selection is made.
        In Qt, we call on_selection_changed which calls like this:
            on_selection_changed(selected_items, deselected_items)

        While we may not be actively doing something with deselect, we do need
        to pass it -- ignoring it for now.

        Args:
            - Selected: The path of the item selected
            - Deselected: (Ignored)
        Returns:
            - (Indirect) Changes selection in user tree graphically.
        Relationship(s):
            - None
        """
        if not selected.indexes():
            self.selected_label.setText("No item selected")
            return
        index = selected.indexes()[0]
        path = self.model.filePath(index)
        p = Path(path)
        prefix = "(Folder) " if p.is_dir() else ""
        self.selected_label.setText(prefix + path)

    # ==== ACTIONS ====
    def rename_selected(self):
        # TODO: Figure out a double-click mechanism here if the file is one of
        # loop or track.
        """
        Description: Renames a file. User must click on the file to select it,
        then click the "Rename Selected" button to use.
        Args:
            - None
        Returns:
            - (Indirect) Renamed file.
        Relationship(s):
            - None
        """
        src = self._current_path()

        # If path isn't usable, provide a message!
        if not src:
            QMessageBox.information(self, "Rename",
                                    "Select a file or folder first.")
            return

        # Creates a small pop-up to rename
        new_name, rename_complete = QInputDialog.getText(
            self, "Rename", "New name:", text=src.name
        )

        # Uses above bool to determine if user followed-through on rename
        # If not, ignores attempt and completes process
        if not rename_complete or not new_name.strip():
            return

        # Otherwise, checks that new name isn't already in directory as another
        # file.
        dst = src.with_name(new_name.strip())
        if dst.exists() and dst != src:
            QMessageBox.warning(self, "Rename",
                                f"'{new_name}' already exists here.")
            return

        # Finally, renames the file.
        try:
            src.rename(dst)
            self.status.showMessage(f"Renamed to: {dst.name}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Rename", f"Failed to rename:\n{e}")

    def trash_selected(self):
        """
        Description: Trashes a file. Uses send2trash to do so.
        Args:
            - None
        Returns:
            - (Indirect) File is removed from directory.
        Relationship(s):
            - None
        """
        # Grabs path
        path = self._current_path()
        if not path:
            QMessageBox.information(self, "Move to Trash",
                                    "Select a file or folder first.")
            return

        label = "folder" if path.is_dir() else "file"

        # UI to prevent accidental delete
        resp = QMessageBox.warning(
            self,
            "Move to Trash",
            f"Really move this {label} to Trash?\n\n{path}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        # Abandon delete if user selects "yes"
        if resp != QMessageBox.Yes:
            return

        # Otherwise, use send2trash to delete file.
        try:
            send2trash(str(path))
            self.selected_label.setText("No item selected")
            self.status.showMessage(f"Moved {label} to Trash.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Move to Trash",
                                 f"Failed to move to Trash:\n{e}")


def main():
    app = QApplication(sys.argv)
    w = FileTreeBrowser()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
