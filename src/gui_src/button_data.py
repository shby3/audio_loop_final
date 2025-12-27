from PySide6.QtGui import QKeySequence
from loop import Loop
from track import Track

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

# New loop
tracks = {
        1: Track(track_name="Track 1"),
        2: Track(track_name="Track 2", track_filepath="../projects/recordings/kick.aif"),
        3: Track(track_name="Track 3", track_filepath="../projects/recordings/snare.aif"),
        4: Track(track_name="Track 4", track_filepath="../projects/recordings/scale.aif"),
        5: Track(track_name="Track 5"),
        6: Track(track_name="Track 6")
    }
loop = Loop(loop_tracks=tracks)


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


def make_track_button(track_num, button_dict):
    """
    Take in an int 1-6 and a button dict and make the button specific to that
    track. Return a new dict with a key for the track number.
    """
    new_dict = button_dict.copy()
    new_dict["track"] = track_num

    # Take function given from dict but utilize track number
    def new_handler():
        default_handler(f"{new_dict['key']} {track_num}")
        button_dict["handler"](track_num)
    # Have new handler print track number and handle it
    new_dict["handler"] = new_handler
    return new_dict


def handle_record():
    loop.is_recording = not loop.is_recording
    default_handler("record_loop")
    print(f"Loop recording = {loop.is_recording}")


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
    "action": None,
    "button": None,
    "shortcut": None,
    "handler": lambda: default_handler("clear_track"),
}

delete_track = {
    "key": "delete_track",
    "icon": (ICON_PATH + "delete_track_icon.svg"),
    "tooltip": "Delete track",
    "action": None,
    "button": None,
    "shortcut": QKeySequence.Delete,
    "handler": lambda: default_handler("delete_track"),
}

delete_loop = {
    "key": "delete_loop",
    "icon": (ICON_PATH + "delete_loop_icon.svg"),
    "tooltip": "Delete loop",
    "action": None,
    "button": None,
    "shortcut": None,
    "handler": lambda: default_handler("delete_loop"),
}

export_loop = {
    "key": "export_loop",
    "icon": (ICON_PATH + "export_loop_icon.svg"),
    "tooltip": "Export loop",
    "action": None,
    "button": None,
    "shortcut": QKeySequence.Save,
    "handler": lambda: default_handler("export_loop"),
}

help_menu = {
    "key": "help_menu",
    "icon": (ICON_PATH + "help_menu_icon.svg"),
    "tooltip": "Open help menu",
    "action": None,
    "button": None,
    "shortcut": QKeySequence.HelpContents,
    "handler": lambda: default_handler("help_menu"),
}

loop_menu = {
    "key": "loop_menu",
    "icon": (ICON_PATH + "loop_menu_icon.svg"),
    "tooltip": "Loop Menu",
    "action": None,
    "button": None,
    "shortcut": None,
    "handler": lambda: default_handler("loop_menu"),
}

mute_track = {
    "key": "mute_track",
    "icon": (ICON_PATH + "mute_icon.svg"),
    "tooltip": "Mute track",
    "action": None,
    "button": None,
    "shortcut": None,
    "handler": lambda: default_handler("mute_track"),
}

mute_loop = {
    "key": "mute_loop",
    "icon": (ICON_PATH + "mute_icon.svg"),
    "tooltip": "Mute loop",
    "action": None,
    "button": None,
    "shortcut": None,
    "handler": lambda: default_handler("mute_loop"),
}

name_track = {
    "key": "name_track",
    "icon": (ICON_PATH + ""),
    "tooltip": "Rename current track",
    "action": None,
    "button": None,
    "shortcut": None,
    "handler": lambda: default_handler("name_track"),
}

new_loop = {
    "key": "new_loop",
    "icon": (ICON_PATH + "new_loop_icon.svg"),
    "tooltip": "Create new loop",
    "action": None,
    "button": None,
    "shortcut": QKeySequence.New,
    "handler": lambda: default_handler("new_loop"),
}

play_track = {
    "key": "play_track",
    "icon": (ICON_PATH + "play_icon.svg"),
    "tooltip": "Play track",
    "action": None,
    "button": None,
    "shortcut": None,
    "handler": lambda: default_handler("play_track"),
}

play_loop = {
    "key": "play_loop",
    "icon": (ICON_PATH + "play_icon.svg"),
    "tooltip": "Play loop",
    "action": None,
    "button": None,
    "shortcut": QKeySequence("Ctrl+Space"),
    "handler": lambda: default_handler("play_loop", loop.play),
}

record_loop = {
    "key": "record_loop",
    "icon": (ICON_PATH + "record_icon.svg"),
    "tooltip": "Record loop",
    "action": None,
    "button": None,
    "shortcut": QKeySequence("Ctrl+R"),
    "handler": handle_record,
}

redo = {
    "key": "redo",
    "icon": (ICON_PATH + "redo_icon.svg"),
    "tooltip": "Redo",
    "action": None,
    "button": None,
    "shortcut": QKeySequence.Redo,
    "handler": lambda: default_handler("redo"),
}

stop_loop = {
    "key": "stop_loop",
    "icon": (ICON_PATH + "stop_icon.svg"),
    "tooltip": "Stop loop",
    "action": None,
    "button": None,
    "shortcut": QKeySequence("Ctrl+Space"),
    "handler": lambda: default_handler("stop_loop", loop.stop),
}

undo = {
    "key": "undo",
    "icon": (ICON_PATH + "undo_icon.svg"),
    "tooltip": "Undo",
    "action": None,
    "button": None,
    "shortcut": QKeySequence.Undo,
    "handler": lambda: default_handler("undo"),
}

select_track = {
    "key": "select_track",
    "icon": (ICON_PATH + "record_icon.svg"),
    "tooltip": "Select this track for recording",
    "action": None,
    "button": None,
    "shortcut": None,
    "handler": loop.set_recording_track,
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
    "clear_track": clear_track,
    "mute_track": mute_track,
    "select_track": select_track
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

# Add a toolbar for each track
for n in range(1, 7):
    new_track_buttons = TrackButtons.copy()
    for key in new_track_buttons.keys():
        button = new_track_buttons[key]
        new_track_buttons[key] = make_track_button(n, button)
    Toolbars.append((f"Track {n}", new_track_buttons, "top", True))
