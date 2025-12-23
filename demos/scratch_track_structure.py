"""This is a working file for a potential data structure of the loop in a
dictionary.
The loop structure is saved in Loop. Each track is saved as a TrackNode.

NOTE: some of these functions and structure may need to be omitted as the app
progresses and as the data structure
Author: Daniel Kaufman"""


class TrackNode:
    """
    Description:
        Node in a singly linked list of audio tracks. Each node represents one
        track
        (e.g., a loop file) and stores file metadata, playback/modulation
        flags, and
        a pointer to the next track.

    Args:
        - None: Instances are initialized with default values; properties can
        be set via setters.

    Methods:
       - get_filepath() -> Optional[str]: Get the path to the associated audio
       file.
       - set_filepath(filepath: str) -> None: Set the path to the associated
       audio file.
       - add_track(file) -> None: Append a new TrackNode at the end of the
       list.
       - delete(track_number: int) -> None: Remove the track with the given
       number; raises IndexError if not found.
       - mute_track(track_number: int) -> None: Mute the specified track.
       - unmute_track(track_number: int) -> None: Unmute the specified track.
       - set_file_location(location: str) -> None: Alias for setting the file
       path.
       - set_name(new_name: str) -> None: Set a user-defined name for this
       track.
       - get_file_location() -> Optional[str]: Return the file path for this
       track.
       - get_length() -> int: Return the track duration (in f
       rames/samples/units as defined elsewhere).

    Relationship(s):
        - Contained in: a Loop (linked-list head managed externally, e.g.,
        Loop.head).
        - Links to: next -> TrackNode | None (singly linked list of tracks).
    """

    def __init__(self):
        self._length = 0
        self._channels = None
        self._mute = False
        self._filepath = None
        self._name = None  # user defined name
        self._file = None
        self._pitch_modulation = None
        self._time_dilation = None
        self._reverse = False
        self._waveform_image = None
        self.next = None
        self.track_number = 0
        self.volume = 0  # out of 100

    def get_filepath(self):
        return self._filepath

    def set_filepath(self, filepath):
        self._filepath = filepath

    def add_track(self, file):
        """This function adds a new track to the end of the linked list"""
        # TODO - limit to 4 for now?
        if self.next is None:
            self.next = TrackNode()
            self.next.track_number = self.track_number + 1
            # TODO: add file data (length, loc)
            # TODO: set_filepath()
        else:
            self.next.add_track(file)
        return

    def delete(self, track_number: int):
        """This function deletes a specified track from the linked list"""
        if track_number == 1:
            Loop.head = self.next
            return
        while self.track_number + 1 < track_number:
            self.next.delete(track_number)
        if self.next is None:
            raise IndexError(
                "Track number " + str(track_number) + " does not exist"
            )
        self.next = self.next.next
        # TODO: Insert file delete instructions here
        return

    def mute_track(self, track_number: int):
        """Mute a track"""
        current_track = self
        try:
            while current_track.track_number < track_number:
                current_track = current_track.next
        except FileNotFoundError:
            "Track does not exist"
        self._mute = True
        return

    def unmute_track(self, track_number: int):
        """Unmute a track"""
        current_track = self
        while current_track.track_number < track_number:
            current_track = current_track.next
        self._mute = False
        return

    def set_file_location(self, location: str):
        """Sets location of a file associated with this track"""
        self._filepath = location

    def set_name(self, new_name: str):
        """Renames a track"""
        self._name = new_name

    def get_file_location(self):
        """Return the location of the file associated with this track"""
        return self._filepath

    def get_length(self):
        """Return the duration of the track file"""
        return self._length


class Loop:
    """
    Description:
        Container class that manages a linked list of TrackNode objects,
        representing
        a collection of audio tracks within a loop. Provides methods for
        adding,
        deleting, renumbering, muting, and managing overall loop-level
        properties
        such as master volume and global mute state.

    Args:
        - None: Instances are initialized with default loop parameters and no
        tracks.

    Methods:
       - get_track_count() -> int:
            Return the number of tracks currently in the loop.
       - mute_all_tracks() -> None:
            Mute all tracks in the loop.
       - unmute_all_tracks() -> None:
            Unmute all tracks in the loop.
       - delete_all_tracks() -> None:
            Delete all tracks and reset the loop to an empty state.
       - delete_track(track_number: int) -> None:
            Delete a specific track, renumber remaining tracks, and update the
            track count.
       - add_first_track() -> None:
            Add the initial track to an empty loop.
       - renumber_tracks() -> None:
            Sequentially renumber tracks after a deletion to maintain
            continuity.
       - save_track_list() -> None:
            (Placeholder) Save the loop’s current track list to a persistent
            format (e.g., pickle).
       - load_track_list() -> None:
            (Placeholder) Load a previously saved track list from a persistent
            format.

    Relationship(s):
        - Contains: TrackNode (head → linked list of TrackNodes)
        - May be referenced by: TrackNode.delete() when resetting head pointer
    """

    def __init__(self):
        self.head = None
        self.track_count = 0
        self.mute_all_tracks = False
        self.master_vol_left = 10
        self.master_vol_right = 10

    def get_track_count(self):
        """Returns the number of tracks in the list"""
        return self.track_count

    def mute_all_tracks(self):
        """Mutes all tracks"""
        self.mute_all_tracks = True

    def unmute_all_tracks(self):
        """Unmutes all tracks"""
        self.mute_all_tracks = False

    def delete_all_tracks(self):
        """This function deletes all tracks"""
        current_track = self.head
        while current_track is not None:
            current_track.delete_track(1)
            current_track = current_track.next
        self.head = None
        self.track_count = 0
        self.mute_all_tracks = False
        return

    def delete_track(self, track_number):
        """This function renumbers all tracks after a track deletion and
        resets track count in the track list"""
        self.head.delete(track_number)
        self.head.renumber_tracks(track_number)
        self.track_count = self.track_count - 1

    def add_first_track(self):
        """This function adds a first track to the end of the linked list"""
        if self.get_track_count() == 0:
            self.head = TrackNode()
            # TODO add soundfile to track
            self.track_count += 1
            self.head.track_number = 1

    def renumber_tracks(self):
        """This function renumbers all tracks after a track deletion"""
        current_track = self.head
        if current_track is None:
            raise FileNotFoundError("No tracks exist in list loop")
        current_track.track_number = 1
        while current_track.next is not None:
            current_track.next.track_number = current_track.track_number + 1
            current_track = current_track.next
        return

    def save_track_list(self):
        # TODO
        pass

    def load_track_list(self):
        # TODO - de-pickle
        pass
