# src/__init__.py
"""
+++------------------------------------------------------------------------+++
This file sets up the package exports for the src directory
Lets us have simpler submodule imports directly from src
i.e.
            from src import play_track_file
                    instead of:
    from src.audio_src.play_functions import play_track_file

NOTE: noqa: F401, F403 comments are to make flake8 not complain about the
      imports being unused in this file and using 'import *'.
+++------------------------------------------------------------------------+++
"""
from . import audio_src, gui_src
from .audio_src import *  # noqa: F401,F403
from .gui_src import *  # noqa: F401,F403

__all__ = [
    *audio_src.__all__,
    *gui_src.__all__,
]
