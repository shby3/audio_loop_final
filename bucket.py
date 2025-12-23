from dataclasses import dataclass
import exceptions as e
from enum import Enum

from loop import Loop
from file_manager import FileManager


"""
+++------------------------------------------------------------------------+++
Defines a Bucket class and all related methods. Generally, this bucket
class is responsible for immediate playback of a loop object. The goal for a
bucket is one of testing / experimentation. This allows for audio playback of a
given loop without having to load it to the loop design area. Buckets have
built-in tooling for at-a-glance track availability, and playback -- not much
else.

Written by: Michelle Mann
+++------------------------------------------------------------------------+++
"""


class BucketState(Enum):
    """
    Defines specific play states of a bucket.
    """
    EMPTY = "empty"
    PLAYING = "playing"
    STOPPED = "stopped"
    PAUSED = "paused"


@dataclass
class Bucket:
    """
    Description: Represents a bucket object. Buckets are pointed to a given
    .loop file path and offer immediate playback functionality outside of the
    loop design area.

    NOTE: At any given time only 10 buckets are available to the user. So
    renaming buckets is not something that we need to think about!

    Args:
        - bucket_id (int): Represent the name of the bucket. Bucket names are
                                        ints between 0 and 9.
        - is_bucket_active (bool): A boolean representing whether or not a loop
                                        has been pointed to a given bucket. If
                                        False, the bucket is considered "empty"
                                        and a given loop can be pointed to it.
                                        If True, the bucket is considered
                                        "full" and the loop object can be set
                                        to playback if desired.
        - mapped_loop (Loop): A loop mapped to the bucket for playback.
        - loop_display_name (string): Represents the display name of a loop
                                        object. This is the human-given name
                                        given to a loop for organizational
                                        purposes.
        - loop_path: (string): Represents the file path of the .loop object.
                                        This is the computer-given name created
                                        when the loop object was initialized.
        - is_track_filled (dict<int: bool>): A dictionary of booleans that map
                                        a given loop's track positions to
                                        whether or not they're filled - False
                                        for "empty" and True for "filled".
        - bucket_state (enums): The state of the bucket that can be used to
                                        track play back, stopping, and paused
                                        states.
    Methods:
    - get_bucket_id(): Returns integer associated as the bucket's name.
    - get_is_bucket_active(): Returns a boolean associated with if the bucket
                                        possesses a mapped loop to it or not.
                                        True if yes, False if no. Defaults to
                                        False (an empty state).
    - set_is_bucket_active(): Toggles whether the bucket is marked 'active' or
                                        not. True -> False or False -> True.
    - get_mapped_loop(): Returns mapped loop object.
    - get_loop_display_name(): Returns the user-given name of the loop
                                        associated with the bucket.
    - set_loop_display_name(name): When a bucket is mapped with a loop, stores
                                        the loop name as a part of the bucket
                                        for recall.
    - get_loop_path(): Returns the computer-created path of the loop associated
                                        with the bucket.
    - set_loop_path(path): When a bucket is mapped with a loop, stores
                                        the loop path as a part of the bucket
                                        for recall.
    - get_bucket_state(): Returns the BucketState associated with the bucket.
    - set_bucket_state(state): Sets the associated BucketState as empty,
                                        stopped, playing or paused.
    - _mark_empty(): Sets the BucketState as empty
    - _mark_playing(): Sets the BucketState as playing
    - _mark_stopped(): Sets the BucketState as stopped
    - _mark_paused(): Sets the BucketState as paused.
    - get_is_track_filled(track): Returns if a given track in the mapped loop
                                        is filled (True if so, False if not.)
    - set_are_tracks_filled(loop): Takes the mapped loop and updates all track
                                        positions in is_track_filled.
    - display_track_indicators(): Returns a tuple of the booleans related to
                                        is_track_filled. Used for indicators on
                                        the bucket.
    - clear_bucket(): Restores bucket to original state.

    Relationship(s):
        - Called by Controller and GUI.
    """

    def __init__(self, bucket_id,
                 is_bucket_active=False,
                 mapped_loop=None,
                 loop_display_name=None,
                 loop_path=None,
                 bucket_state=BucketState.EMPTY):
        """
        Initializes a bucket object.
        """

        self.bucket_id = bucket_id
        self.is_bucket_active = is_bucket_active
        self.bucket_state = bucket_state

        self.mapped_loop = mapped_loop
        self.loop_display_name = loop_display_name
        self.loop_path = loop_path

        self.is_track_filled = {
            1: False,
            2: False,
            3: False,
            4: False,
            5: False,
            6: False
        }

    # We do not need a setter program for bucket_id as renaming a bucket isn't
    # an option.
    def get_bucket_id(self) -> int:
        """
        Description: Returns the bucket_id of the bucket it is passed to.
        Args:
            - None.
        Returns:
            - bucket_id (int): The integer mapping id of the bucket. It's name.
        Relationship(s):
            - None.
        """
        return self.bucket_id

    def get_is_bucket_active(self) -> bool:
        """
        Description: Returns if the bucket is empty / active or not (active
        referring to the button state). Empty or inactive refers to if the
        bucket has a mapped loop associated with it. False, if not, True if it
        does. Defaults to False.
        Args:
            - None.
        Returns:
            - is_bucket_active (bool): A boolean if the bucket has a mapped
            loop associated with it (or not). False if not, True if so.
            Defaults to False.
        Relationships(s):
            - Need this to determine if a user is trying to remap a new loop to
            a bucket that already has a mapped loop in it!
        """
        return self.is_bucket_active

    def set_is_bucket_active(self) -> None:
        """
        Description: Changes the state of whether the bucket is considered
        active. If currently active (True), toggles to inactive (False),
        otherwise, toggles from inactive (False) to active (True).
        Args:
            - None.
        Returns:
            - None.
            - [Action] changes state of is_bucket_active from T -> F or F -> T.
        Relationship(s):
            - This should be called when bucket is mapped to a loop.
        """
        active_bucket = self.get_is_bucket_active()

        if not active_bucket:
            self.is_bucket_active = True
        else:
            self.is_bucket_active = False

    def get_mapped_loop(self) -> Loop:
        """
        Description: Returns the associated mapped loop from the bucket.
        Args:
            - None.
        Returns:
            - mapped_loop (Loop): The associated loop to the bucket.
        Relationship(s):
            - None.
        """
        return self.mapped_loop

    def set_mapped_loop(self, loop_path: str) -> None:
        """
        Description: Maps a loop object to this bucket.
        Args:
            - loop_path (string): The path of a given loop. If provided, is
            deserialized into a Loop object and held at mapped_loop.
        Returns:
            - None:
            - [Action]: sets mapped_loop to the loop object.
        Relationship(s):
            - Required for mapping loop.
        """
        if not loop_path:
            raise e.InvalidLoop(f"Given loop path is not valid: {loop_path}")

        fm = FileManager()
        loop = fm.deserialize_loop(loop_path)

        self._assign_loop(loop)

    def get_loop_display_name(self) -> str:
        """
        Description: Returns the loop_display_name associated with the bucket's
        mapped loop.
        Args:
            - None.
        Returns:
            - loop_display_name (string): The user-chosen display name
            associated with a given mapped loop.
        Relationship(s):
            - Calls is_active_loop before being returning items to determine if
            bucket actually has a mapped loop.
        """
        return self.loop_display_name

    def set_loop_display_name(self, name) -> None:
        """
        Description: Upon mapping a loop to the bucket, sets the loop_display_
        name variable to the loop_display_name of the loop.
        Args:
            - name (string): The display_name of the loop.
        Returns:
            - None.
            - [Action] Sets the loop_display_name variable to the included name
        Relationship(s):
            - Updated upon mapping the bucket to a known loop.
        """
        if name:
            self.loop_display_name = name
        else:
            raise e.InvalidLoop("This loop doesn't actually exist.")

    def get_loop_path(self) -> str:
        """
        Description: Returns the loop_path associated with the bucket's
        mapped loop.
        Args:
            - None.
        Returns:
            - loop_path (string): The computer-generated loop name associated
            with a given loop.
        Relationship(s):
            - Calls is_active_loop before being returning items to determine if
            bucket actually has a mapped loop.
        """
        return self.loop_path

    def set_loop_path(self, path) -> None:
        """
        Description: Upon mapping a loop to the bucket, sets the loop_path
        variable to the loop_path of the loop.
        Args:
            - path (string): The computer-generated loop name associated
            with a given loop.
        Returns:
            - None.
            - [Action] Sets the loop_path variable to the included path
        Relationship(s):
            - Updated upon mapping the bucket to a known loop.
        """
        if path:
            self.loop_path = path
        else:
            raise e.InvalidLoop("This loop doesn't actually exist.")

    def get_bucket_state(self) -> Enum:
        """
        Description: Returns the bucket state prior to attempting playback etc.
        Args:
            - None.
        Returns:
            - bucket_state (Enum): The state of the bucket. Either:
            "Empty", "Playing", "Stopped" or "Paused".
        Relationship(s):
            - Should be called for checks on whether the bucket is empty or not
            or if toggling between playing and stop / pause. A bucket set to
            "playing" does not need to be played. Likewise, a bucket set to
            "stopped" or "paused" does not need to be set to either. We only
            care about changing the bucket's state when it is not the state
            we're in!
        """
        return self.bucket_state

    def set_bucket_state(self, state: BucketState) -> None:
        """
        Description: Sets the state of the bucket upon change.
        Args:
            - state (Enum): A BucketState state.
        Returns:
            - None:
            - [Action] Sets the bucket_state appropriate in the bucket object.
        Relationship(s):
            - Should be called for checks on whether the bucket is empty or not
            or if toggling between playing and stop / pause. A bucket set to
            "playing" does not need to be played. Likewise, a bucket set to
            "stopped" or "paused" does not need to be set to either. We only
            care about changing the bucket's state when it is not the state
            we're in!
        """
        if not isinstance(state, BucketState):
            raise TypeError(f"state must be a BucketState, got {type(state)}")

        if self.bucket_state is state:
            raise e.InvalidState(f"Bucket is already in state {state.value}.")
        else:
            self.bucket_state = state

    def _mark_empty(self) -> None:
        """
        Description: Designates a bucket as "empty". This happens either upon
        the creation of the bucket at app startup, or removal of mapped loop to
        the bucket itself.
        Args:
            - None.
        Returns:
            - None.
            - [Action] Sets BucketState to "empty".
        Relationship(s):
            - Used for determining if an action can be performed on a bucket.
        """
        self.set_bucket_state(BucketState.EMPTY)

    def _mark_paused(self) -> None:
        """
        Description: Designates a bucket as "paused". This can only happen
        going from a playback state into paused.
        Args:
            - None.
        Returns:
            - None.
            - [Action] Sets BucketState to "paused".
        Relationship(s):
            - Used for determining if an action can be performed on a bucket.
        """
        self.set_bucket_state(BucketState.PAUSED)

    def _mark_playing(self) -> None:
        """
        Description: Designates a bucket as "playing". This can only happen
        going from a paused or stopped state into playing.
        Args:
            - None.
        Returns:
            - None.
            - [Action] Sets BucketState to "playing".
        Relationship(s):
            - Used for determining if an action can be performed on a bucket.
        """
        self.set_bucket_state(BucketState.PLAYING)

    def _mark_stopped(self) -> None:
        """
        Description: Designates a bucket as "stopped". This can only happen
        going from a paused or playing state into stopped.
        Args:
            - None.
        Returns:
            - None.
            - [Action] Sets BucketState to "stopped".
        Relationship(s):
            - Used for determining if an action can be performed on a bucket.
        """
        self.set_bucket_state(BucketState.STOPPED)

    def get_is_track_filled(self, track) -> bool:
        """
        Description: Returns whether or not a given track associated with the
        mapped loop in a bucket is filled. Returns True if so, False if not.
        Args:
            - track (int): The numeric name of a track associated with a mapped
            loop in a bucket.
        Returns:
            - is_track_filled (bool): True if so, False if not.
        Relationship(s):
            - Used for indicator lights -- nothing else.
        """
        return self.is_track_filled[track]

    def set_are_tracks_filled(self, loop: Loop) -> None:
        """
        Description: Toggles an individual track's indicator for filled. If in
        the given loop a track is being used, ensure that the respective
        is_track_filled location is represented correctly.
        Args:
            - loop (Loop): The mapped loop in a bucket.
        Returns:
            - None.
            - [Action] Updates all is_track_filled locations based on the loop.
        Relationship(s):
            - Used for indicator lights -- nothing else.
        """
        # Loop through all tracks in the loop, if a track exists in a position,
        # return True, otherwise, False.
        self.is_track_filled = {
            pos: (track is not None)
            for pos, track in loop.loop_tracks.items()
        }

    def _assign_loop(self, loop: Loop) -> None:
        """
        Description: This is a helper function that sets the mapped_loop on
        this bucket by setting the display_name, loop_path and is_track_filled
        parameters appropriately.
        Args:
            - loop (Loop): The loop object we're mapping to the bucket.
        Returns:
            - None.
            - [Action]: Sets loop_display_name, loop_path, and is_track_filled
            = [Action]: Sets is_bucket_active to True
        Relationship(s):
            - Required process for mapping a loop to a loop object.
        """
        self.mapped_loop = loop
        self.set_loop_display_name(loop.get_loop_display_name())
        self.set_loop_path(loop.get_loop_id())
        self.set_are_tracks_filled(loop)

    def display_track_indicators(self) -> tuple:
        """
        Description: Returns a tuple related to the six tracks in a loop and
        whether they are full.
        Args:
            - None.
        Returns:
            - is_full (tuple): A tuple like this:
                (True, True, False, False, False, True) that represents full
                tracks associated with the mapped_loop.
        Relationship(s):
            - Used for the express purposes of indicators on the bucket.
        """
        return tuple(self.is_track_filled[i]
                     for i in sorted(self.is_track_filled))

    def clear_bucket(self) -> None:
        """
        Description: Restores bucket to original state.
        Args:
            - None.
        Returns:
            - None.
            - [Action]: Bucket is restored to original state.
        Relationship(s): Used in delete or clear for bucket.
        """
        self.is_bucket_active = False
        self.mapped_loop = None
        self.loop_display_name = None
        self.loop_path = None
        self.bucket_state = BucketState.EMPTY

        self.is_track_filled = {
            1: False,
            2: False,
            3: False,
            4: False,
            5: False,
            6: False
        }
