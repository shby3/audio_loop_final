"""An area to create specific errors related to our codebase.
Written by: Michelle Mann
"""


class RecordingError(Exception):
    """Base class for recording-related errors."""


class OverwriteError(RecordingError):
    """Raised when a user attempts to overwrite an already existing slot in
    a loop."""


class NonExistantTrackError(RecordingError):
    """Raised when a user attempts to record outside of the loop's six tracks.
    """


class MissingComponentError(Exception):
    """Base class for missing component-related errors."""


class MissingRecorderError(MissingComponentError):
    """Raised when a recording is attempted without a recording device."""


class InvalidLoop(Exception):
    """Raised when a loop is called and doesn't actually exist."""


class InvalidState(Exception):
    """Raised when an attempt to load an item is requested without 'LOAD'
    button"""


class InvalidRequest(Exception):
    """Raised when a request is made against an empty item (i.e. get_name etc.)
    """
