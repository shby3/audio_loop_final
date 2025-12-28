"""
Validator component -- button clicks for application are grabbed from GUI,
passed to this app to ensure controller components are valid requests,
then passes back to controller for execution.
Written by: Michelle Mann
"""

from src.classes.loop import Loop
from src.classes import exceptions as e


# import pathlib as path


class Validator:
    """
    Represents a validator application. Takes execution instructions from
    GUI, then passes instructions here for validation. Communications

    Args:
        [None]

    Methods:
        - is_valid_loop(loop: Loop): Takes a loop object and validates whether
                                    or not it is a valid Loop object. If none,
                                    returns False.
        - get_extension(obj: Loop or Track): Takes a Loop or Track object and
                                    returns the file extension associated with
                                    the object.
        - is_recordable(channel_config, track_position, active_loop): Validates
                                    if stereo or mono recording is valid in
                                    requested recording position.
    """

    def __init__(self):
        """A single Validator component"""
        pass

    def is_valid_loop(self, loop: Loop):
        if loop:
            return True
        return False

    def get_extension(self, obj):
        """
        Description: Returns the file type associated with an object.
        Arg:
            - obj (Object: Loop / Track): the object
        Returns:
            - An extension (string): either .loop or .track depending on the
                                    object passed.
        Relationship(s):
            - Called in loading or moving an object.
        """
        if obj.endswith(".track"):
            return "track"
        else:
            return "loop"

    def is_recordable(self, channel_config, track_position, active_loop):
        """
        Checks to ensure that a recording request is valid.
        """
        # Identify all potential tracks
        if channel_config == 2:
            track1 = track_position
            track2 = track_position + 1

        # Raise error for recording in invalid track.
        elif channel_config == 2 and track1 == 6:
            raise e.NonExistantTrackError(f"You can't record stereo to \
                track {track1}")

        # Ensure tracks are available for recording
        # If mono and a valid track 1-6, record to single track.
        elif channel_config == 1 and not active_loop[track1]:
            return (track1)

        # If stereo and a valid track 1-5 (there is no 7, so we can't record in
        # 6), record.
        elif (channel_config == 2 and track1 <= 5) and \
                (active_loop[track1] and active_loop[track2]):
            return (track1, track2)

        else:
            raise e.NonExistantTrackError("Error in recording location.")

    def is_loop_area(location) -> bool:
        """
        Description: Returns if the location provided is part of the loop
        design area.
        Args:
            - location (string): The name of the location.
        Returns:
            - Bool: True if location is in loop design area, or False if not.
        Relationship:
            - Called by load or move functions in controller.
        """
        # Loop Area Locations are names
        loop_area_locations = set("Track1",
                                  "Track2",
                                  "Track3",
                                  "Track4",
                                  "Track5",
                                  "Track6",
                                  "LoopVolumeArea")

        # If location is in loop_area_location, location is in loop design area
        return location in loop_area_locations

    def is_bucket(location) -> bool:
        """
        Description: Returns if the location provided is part of the loop
        buckets area.
        Args:
            - location (string): The name of the location.
        Returns:
            - Bool: True if location is in loop buckets area, or False if not.
        Relationship:
            - Called by load or move functions in controller.
        """
        # Loop Area Locations are names
        loop_bucket_area = set("Bucket1",
                               "Bucket2",
                               "Bucket3",
                               "Bucket4",
                               "Bucket5",
                               "Bucket6",
                               "Bucket7",
                               "Bucket8",
                               "Bucket9",
                               "Bucket10",
                               "LoopBucketArea")

        # If location is in loop_area_location, location is in loop design area
        return location in loop_bucket_area
