# src/audio_src/__init__.py
"""
+++------------------------------------------------------------------------+++
This file sets up the package exports for the audio_src directory
NOTE: noqa: F401 comments are to make flake8 not complain about the imports
      being unused in this file.
+++------------------------------------------------------------------------+++
"""
from . import play_functions, record_functions

from .play_functions import (  # noqa: F401
    play_track_file,
    play_track_buffer,
    mix_track_buffers,
)
from .record_functions import (  # noqa: F401
    generate_track_path,
    record_track,
    merge_track_buffers,
)

from .echo import echo  # noqa: F401

__all__ = [*play_functions.__all__, *record_functions.__all__, "echo"]
