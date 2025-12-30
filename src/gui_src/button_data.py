import json

from PySide6.QtGui import QKeySequence
from PySide6.QtCore import QThread, Signal
from copy import deepcopy
from functools import partial

from PySide6.QtWidgets import QInputDialog, QLineEdit

VOLUME_LIMIT = 8.0

"""
+++------------------------------------------------------------------------+++
This file contains data structures that hold the information needed to
create buttons for the application. Each button has its own standalone
info dictionary that is referenced in area specific nested dictionaries.
For example, the button mute_loop has a small standalone dictionary. The
nested reference dictionary AllButtonsDict includes the key "mute_loop" and
its value is a pointer to the mute_loop standalone dictionary.
+++------------------------------------------------------------------------+++

For now, Loops are maintained here so that button handlers can easily be connected
to Loop and Track operations.
"""
# defines public modules for importing between directories
__all__ = [
    "Toolbars",
    "AllButtonsDict",
    "TransportButtons",
    "TrackButtons",
    "LoopButtons",
]

import os

# Get the directory of this file and construct the icon path
ICON_PATH = os.path.join(os.path.dirname(__file__), "icon_src") + os.sep

# Tracks recorded onto when loop was last playing. When record is stopped, these are cleared
# and saved to files.
recorded_tracks = []


class PitchShiftWorker(QThread):
    """ Worker thread to handle pitch shift """
    finished = Signal()

    def __init__(self, track, steps):
        super().__init__()
        self.track = track
        self.steps = steps

    def run(self):
        self.track.pitch_shift(self.steps)
        self.finished.emit()


def default_handler(button_name: str, handler=None):
    """
    Description: Placeholder button action. Prints an informative statement
                 to the terminal when a button is pressed.
    Args:
        - button_name (str): The name of the button being pressed.
        - handler (function): Additional function to be called
        - args (list): Additional arguments to be passed to the handler
    Returns:
        - None.
    Relationship(s):
        - Used as the default handler function stored in button info
          dictionaries.
    """

    print(f"{button_name} pressed.")
    if handler is not None:
        handler()


def handle_record(button_dict):
    default_handler("record_loop")
    loop = button_dict["controller"].loop
    loop.is_recording = not loop.is_recording
    if loop.is_playing and loop.recording_track not in recorded_tracks:
        recorded_tracks.append(loop.recording_track)
    print(f"Loop recording = {loop.is_recording}")


def handle_play(button_dict):
    default_handler("play_loop")
    loop = button_dict["controller"].loop
    loop.play()
    if loop.is_recording and loop.recording_track not in recorded_tracks:
        recorded_tracks.append(loop.recording_track)


def handle_stop(button_dict):
    default_handler("stop_loop")
    loop = button_dict["controller"].loop
    while len(recorded_tracks) > 0:
        t = recorded_tracks.pop()
        loop.get_track(t).generate_track_file()
    loop.stop()


def handle_select_track(button_dict):
    default_handler(f"select_track {button_dict["track"]}")
    loop = button_dict["controller"].loop
    loop.set_recording_track(button_dict["track"])
    if loop.is_recording and loop.is_playing and loop.recording_track not in recorded_tracks:
        recorded_tracks.append(loop.recording_track)


def handle_mute_loop(button_dict):
    default_handler("mute_loop")
    loop = button_dict["controller"].loop
    loop.toggle_mute()


def handle_reverse(button_dict):
    default_handler("reverse_loop")
    loop = button_dict["controller"].loop
    track = button_dict["track"]
    loop.reverse_track(track)


def handle_pan(button_dict):
    default_handler("hand_pan")
    loop = button_dict["controller"].loop
    track = loop.get_track(button_dict["track"])

    # Open up a dialog to adjust track left and right volume
    # Get the name of the project with QInputDialog
    text, ok_pressed = QInputDialog.getText(
        None,  # Parent widget (None for no parent)
        "Adjust left and right volume",  # Dialog title
        "Replace only the numbers with decimal values up to 8.0:",  # Label text
        QLineEdit.Normal,  # Echo mode (e.g., Normal, NoEcho, Password)
        '{"left":1.0, "right":1.0}'  # Default text (empty string here)
    )

    if ok_pressed and text != '':
        try:
            # Make sure left and right are formatted as expected
            pan_data = json.loads(text)
            left = float(pan_data["left"])
            right = float(pan_data["right"])
            # Make sure left and right are less than a limit
            assert left < abs(VOLUME_LIMIT)
            assert right < abs(VOLUME_LIMIT)
            # Apply left and right to track
            track.left = left
            track.right = right
        except Exception as e:
            print(e)


def handle_slip(button_dict):
    default_handler("slip_track")
    loop = button_dict["controller"].loop
    track = loop.get_track(button_dict["track"])

    # Open up a dialog to adjust track left and right volume
    # Get the name of the project with QInputDialog
    text, ok_pressed = QInputDialog.getText(
        None,  # Parent widget (None for no parent)
        "Slip track",  # Dialog title
        "Slip track n frames",  # Label text
        QLineEdit.Normal,  # Echo mode (e.g., Normal, NoEcho, Password)
        'n'  # Default text (empty string here)
    )

    if ok_pressed and text != '':
        try:
            # Make sure text is an int
            fs = int(text)
            # Apply slip
            track.slip(fs)
        except Exception as e:
            print(e)


def handle_clear(button_dict):
    default_handler("clear_track")
    loop = button_dict["controller"].loop
    track = loop.get_track(button_dict["track"])
    track.clear()

"""
+++------------------------------------------------------------------------+++
Standalone button info dictionaries. These dictionaries are nested in curated
area-specific reference dictionaries further in the document.

[-Key / Value Breakdown-]:
    "key"       --> String containing name of the button. Must follow variable
                    naming conventions. This entry is included to make access-
                    ing the standalone dictionaries easier from the nested ref-
                    erence dictionaries.

    "icon"      --> String containing the relative path to the button's icon
                    image file.
    "tooltip"   --> String containing the hover-over tooltip text for the
                    button.
    "action":   --> QAction object representing the command to be triggered
                    when a button is pressed.
    "button":   --> Button object containing the deployable GUI implementation
                    of the button.
    "shortcut": --> String containing the keyboard shortcuts that can be
                    alternately used to activate the button's action.
    "handler": -->  Function defining the sequence of actions to be triggered
                    when a button is pressed.
                    NOTE: a lambda function is used to prevent the function
                    from executing the moment it's accessed.

+++------------------------------------------------------------------------+++
"""


clear_track = {
    "key": "clear_track",
    "icon": (ICON_PATH + "clear_track_icon.svg"),
    "tooltip": "Clears the track",
    "action": handle_clear,
    "button": None,
    "shortcut": None,
    "handler": None,
    "controller": None,
    "track": None,
}

delete_track = {
    "key": "delete_track",
    "icon": (ICON_PATH + "delete_track_icon.svg"),
    "tooltip": "Delete track",
    "action": None,
    "button": None,
    "shortcut": QKeySequence.Delete,
    "handler": lambda: default_handler("delete_track"),
    "controller": None,
}

reverse_track = {
    "key": "reverse_track",
    "icon": (ICON_PATH + "reverse_icon.svg"),
    "tooltip": "Reverse track. Cannot be used while audio is playing.",
    "action": handle_reverse,
    "button": None,
    "shortcut": None,
    "handler": None,
    "controller": None,
}

pan_track = {
    "key": "pan_track",
    "icon": (ICON_PATH + "pan_icon.svg"),
    "tooltip": "Open dialog to adjust audio panning.",
    "action": handle_pan,
    "button": None,
    "shortcut": None,
    "handler": None,
    "controller": None,
}

slip_track = {
    "key": "slip_track",
    "icon": (ICON_PATH + "slip_icon.svg"),
    "tooltip": "Open dialog to slip track. Cannot be used while audio is playing.",
    "action": handle_slip,
    "button": None,
    "shortcut": None,
    "handler": None,
    "controller": None,
}

pitch_track = {
    "key": "pitch_track",
    "icon": (ICON_PATH + "pitch_icon.svg"),
    "tooltip": "Open dialog to adjust pitch. Cannot be used while audio is playing.",
    "action": None,
    "button": None,
    "shortcut": None,
    "handler": None,
    "controller": None,
}

delete_loop = {
    "key": "delete_loop",
    "icon": (ICON_PATH + "delete_loop_icon.svg"),
    "tooltip": "Delete loop",
    "action": None,
    "button": None,
    "shortcut": None,
    "handler": lambda: default_handler("delete_loop"),
    "controller": None,
}

export_loop = {
    "key": "export_loop",
    "icon": (ICON_PATH + "export_loop_icon.svg"),
    "tooltip": "Export loop",
    "action": None,
    "button": None,
    "shortcut": QKeySequence.Save,
    "handler": lambda: default_handler("export_loop"),
    "controller": None,
}

help_menu = {
    "key": "help_menu",
    "icon": (ICON_PATH + "help_menu_icon.svg"),
    "tooltip": "Open help menu",
    "action": None,
    "button": None,
    "shortcut": QKeySequence.HelpContents,
    "handler": lambda: default_handler("help_menu"),
    "controller": None,
}

loop_menu = {
    "key": "loop_menu",
    "icon": (ICON_PATH + "loop_menu_icon.svg"),
    "tooltip": "Loop Menu",
    "action": None,
    "button": None,
    "shortcut": None,
    "handler": lambda: default_handler("loop_menu"),
    "controller": None,
}

mute_track = {
    "key": "mute_track",
    "icon": (ICON_PATH + "mute_icon.svg"),
    "tooltip": "Mute track",
    "action": None,
    "button": None,
    "shortcut": None,
    "handler": lambda: default_handler("mute_track"),
    "controller": None,
    "track": None,
}

mute_loop = {
    "key": "mute_loop",
    "icon": (ICON_PATH + "mute_icon.svg"),
    "tooltip": "Mute loop",
    "action": None,
    "button": None,
    "shortcut": None,
    "handler": lambda: handle_mute_loop(mute_loop),
    "controller": None,
}

name_track = {
    "key": "name_track",
    "icon": (ICON_PATH + ""),
    "tooltip": "Rename current track",
    "action": None,
    "button": None,
    "shortcut": None,
    "handler": lambda: default_handler("name_track"),
    "controller": None,
}

new_loop = {
    "key": "new_loop",
    "icon": (ICON_PATH + "new_loop_icon.svg"),
    "tooltip": "Create new loop",
    "action": None,
    "button": None,
    "shortcut": QKeySequence.New,
    "handler": lambda: default_handler("new_loop"),
    "controller": None,
}

play_track = {
    "key": "play_track",
    "icon": (ICON_PATH + "play_icon.svg"),
    "tooltip": "Play track",
    "action": None,
    "button": None,
    "shortcut": None,
    "handler": lambda: default_handler("play_track"),
    "controller": None,
}

play_loop = {
    "key": "play_loop",
    "icon": (ICON_PATH + "play_icon.svg"),
    "tooltip": "Play loop",
    "action": None,
    "button": None,
    "shortcut": QKeySequence("Ctrl+Space"),
    "handler": lambda: handle_play(play_loop),
    "controller": None,
}

record_loop = {
    "key": "record_loop",
    "icon": (ICON_PATH + "record_icon.svg"),
    "tooltip": "Record loop",
    "action": None,
    "button": None,
    "shortcut": QKeySequence("Ctrl+R"),
    "handler": lambda: handle_record(record_loop),
    "controller": None,
}

redo = {
    "key": "redo",
    "icon": (ICON_PATH + "redo_icon.svg"),
    "tooltip": "Redo",
    "action": None,
    "button": None,
    "shortcut": QKeySequence.Redo,
    "handler": lambda: default_handler("redo"),
    "controller": None,
}

stop_loop = {
    "key": "stop_loop",
    "icon": (ICON_PATH + "stop_icon.svg"),
    "tooltip": "Stop loop",
    "action": None,
    "button": None,
    "shortcut": QKeySequence("Ctrl+Space"),
    "handler": lambda: handle_stop(stop_loop),
    "controller": None,
}

undo = {
    "key": "undo",
    "icon": (ICON_PATH + "undo_icon.svg"),
    "tooltip": "Undo",
    "action": None,
    "button": None,
    "shortcut": QKeySequence.Undo,
    "handler": lambda: default_handler("undo"),
    "controller": None,
}

select_track = {
    "key": "select_track",
    "icon": (ICON_PATH + "record_icon.svg"),
    "tooltip": "Select this track for recording",
    "action": handle_select_track,
    "button": None,
    "shortcut": None,
    "handler": None,
    "controller": None,
    "track": None,
}


"""
+++------------------------------------------------------------------------+++
Area-specific reference dictionaries. These dictionaries store pointers to each
button's standalone info dictionaries. Each reference dictionary stores entries
for buttons grouped to a specific functional area i.e TransportButtons
references buttons used to play/stop/record/etc. an audio track or loop.

[-Key / Value Breakdown-]:
    Keys   --> String containing the name of the button being referenced.
    Values --> Pointer to button's standalone info dictionary used to build it.

+++------------------------------------------------------------------------+++
"""

AllButtonsDict = {
    "clear_track": clear_track,
    "delete_track": delete_track,
    "delete_loop": delete_loop,
    "export_loop": export_loop,
    "help_menu": help_menu,
    "loop_menu": loop_menu,
    "mute_track": mute_track,
    "mute_loop": mute_loop,
    # "name_track": name_track,
    "new_loop": new_loop,
    "play_track": play_track,
    "play_loop": play_loop,
    "record_loop": record_loop,
    "redo": redo,
    "stop_loop": stop_loop,
    "undo": undo,
    "select_track": select_track,
}

TransportButtons = {
    "play_loop": play_loop,
    "record_loop": record_loop,
    "stop_loop": stop_loop,
}

TrackButtons = {
    "select_track": select_track,
    "reverse_track": reverse_track,
    "pan_track": pan_track,
    "slip_track": slip_track,
    "clear_track": clear_track,
}

LoopButtons = {
    "delete_loop": delete_loop,
    "export_loop": export_loop,
    "loop_menu": loop_menu,
    "mute_loop": mute_loop,
    "new_loop": new_loop,
}

UtilityButtons = {"undo": undo, "redo": redo, "help_menu": help_menu}

"""
List of tuples containing a toolbar's name, button dictionary, and desired
window placement respectively.
"""
Toolbars = [
    ("Transport", TransportButtons, "bottom", True),
    ("Utility", UtilityButtons, "top", True),
    ("Loop", LoopButtons, "top", True),
]

# Add a toolbar for each track. Copy 6 of them with added track number.
for n in range(1, 7):
    new_track_buttons = deepcopy(TrackButtons)
    for button_dict in new_track_buttons.values():
        # Add track number to button dict key
        button_dict["key"] = f"{button_dict["key"]}_{n}"
        # Add track number to button dict
        button_dict["track"] = n
        # Update handler for button dict
        button_dict["handler"] = partial(button_dict["action"], button_dict)
        # Add button_dict to AllButtonsDict
        AllButtonsDict[button_dict["key"]] = button_dict

    # Add track toolbar to toolbars
    Toolbars.append((f"Track {n}", new_track_buttons, "top", True))
