from datetime import datetime
import os

DEFAULT_LOOP_NAME = "New Loop"
VALID_POSITIONS = [x for x in range(1, 7)]


class Loop:
    """
    Description:

    Attributes:
        - loop_id(int): A unique identifier for the loop,
        which cannot be changed.
        Naming convention based on loop birth.
        - loop_name(str): The displayed name of the loop.
        - loop_tracks(Dictionary<Int: Track<Obj>>): A dictionary with
        keys 1-6 and values of tracks associated with that track number.
        - loop_length(int): The length of the loop, in seconds.
        Also is the longest track length.
        - displayed_loop_name(str): The displayed name of the loop,
        user defined.
        - is_selected (bool): Whether the loop is currently selected.
        - loop_elapsed_secs (int): The elapsed time of the loop
            (the longest track).
        - loop_birth(str): The birth of the loop, in epochs.

    Methods:
        - check_position(int): Checks if the given position is valid.
        - is_empty(): Checks if the loop is empty or not.
        - get_track_list(): Gets a list of Track objects in the loop.
        - get_loop_display_name(): Returns the display name of the loop.
        - set_loop_display_name(str): Sets the display name of the loop.
        - set_track(obj, int): Sets  track at the given position in the loop.
        dictionary of tracks.
        - remove_track(int): Removes a track at specified position
        - move_track(int, int): Move a track to specified position
        - alter_track(func):
        Uses a Track method to alter a Track in the Loop.
        - set_loop_length(int): Sets the length of the loop, in seconds.
        - set_loop_elapsed_secs(int): Sets the elapsed time of the loop
        - get_loop_length(int): Gets the length of the loop, in seconds.
        - get_loop_selection(bool): Returns if loop is currently selected.
        - toggle_selection(): Toggles selection.
        - get_loop_id(): Returns the ID of the loop currently selected.
        - update_loop() TODO

    Relationship(s):
        -
        The structure is the intermediary between the individual tracks
        and the controller what will act on the tracks.
    """

    def __init__(self, loop_name=DEFAULT_LOOP_NAME, loop_tracks=None) -> None:
        """
        Description: Initializes the loop object.

        args:
            - loop_name(str): The designated name of the loop.
            - loop_tracks(Dictionary<Int: Track<Obj>>):

        Returns: None
        """
        self.loop_birth = datetime.now()
        self._loop_id = f"Loop_{self.loop_birth.strftime("%Y%m%d%H%M%S")}"
        self.loop_name = loop_name
        self.is_selected = False
        self.loop_elapsed_secs = 0
        self.loop_length = 0
        if loop_tracks is None:
            self.loop_tracks = {
                1: None,
                2: None,
                3: None,
                4: None,
                5: None,
                6: None,
            }
        else:
            self.loop_tracks = loop_tracks

    def __repr__(self):
        lines = [f"Loop ID: {self._loop_id}", f"Name: {self.loop_name}"]
        for pos in range(1, 7):
            track = self.loop_tracks[pos]
            lines.append(f"Track {pos}: {track if track else 'Empty'}")
        return "\n".join(lines)

    @staticmethod
    def check_position(position) -> None:
        """
        Description: Checks if the given position is valid.
        Args:
                - position(int): The position to check.
        Returns:
                - ValueError if position is out of range.
        """
        if position not in VALID_POSITIONS:
            raise ValueError("Invalid position")
        else:
            return position

    def is_empty(self) -> bool:
        """
        Description: Checks if the loop is empty or not.
        Args: None
        Returns: bool - True if the loop is empty, False otherwise.

        Relationships:
            - Used by the Controller to check if a Loop cannot be played.
        """
        return all(track is None for track in self.loop_tracks.values())

    def get_track_list(self) -> object:
        """
        Description: Gets a list of Track objects in the loop.
        Args: None
        Returns: A list of Track objects in the loop.

        Relationships:
            - Called by the Controller for its play_loop() method
        """
        return self.loop_tracks.values()

    def get_loop_display_name(self) -> str:
        """
        Description: Returns the display name of the loop.
        Args: None
        Returns: The display name of the loop.

        Relationships:
            - Called by Controller to get the loop name to display on the GUI.
        """
        return self.loop_name

    def set_loop_display_name(self, loop_name: str) -> None:
        """
        Description: Sets the display name of the loop.
        Args: None
        Returns: None
        """
        self.loop_name = loop_name

    def set_track(self, track, position: int) -> None:
        """
        Description: Sets the track at the given position in the loop's
        dictionary of tracks.
        Args:
            track: The track to be used
            position: The position to set the track
        Returns: None

        Relationships:
            - Called by the Controller to set a track in the loop.
        """
        self.loop_tracks[position] = track

    def remove_track(self, position: int) -> None:
        """
        Description: Removes a track at specified position in the loop's
        dictionary of tracks.
        Args:
            position: The position of the track to remove
        Returns: None

        Relationships:
            - Called by the Controller to delete a track.
        """
        self.check_position(position)
        self.loop_tracks[position] = None

    def move_track(self, position_2: int, position_1: int) -> None:
        """
        Description: Move a track to specified position in the loop's
        dictionary of tracks.
        Args:
            position_2 (int): The position of the track to move
            position_1 (int): The new position of the track
        Returns: None

        Relationships:
            - Called by the Controller to move a track.
        """
        # check position exists
        self.check_position(position_1)
        self.check_position(position_2)

        track1 = self.loop_tracks[position_1]
        track2 = self.loop_tracks[position_2]

        # swap if one track is empty
        if track1 is None or track2 is None:
            self.loop_tracks[position_1], self.loop_tracks[position_2] = \
                track2, track1
            print(f"Tracks {position_1} and {position_2} have been swapped")
            return

        # checks if channel configuration is compatible before swapping
        if track1.channel_config() != track2.channel_config():
            raise TypeError(
             f"Cannot swap track position {position_1} with position \
                {position_2}. The track configuration are not")

        self.loop_tracks[position_1], self.loop_tracks[position_2] = \
            track2, track1
        print(f"Tracks {position_1} and {position_2} have been swapped")

    def alter_track(self, position, track_func, params=None) -> None:
        """
        Description: Uses a Track method to alter a Track in the Loop.
        Args:
            -position: The position of the track to alter
            -track_func: The method to use on the track,
            such as mute_track or make_reverse
            -params: The params to pass to the track function
        Returns: None

        Relationships:
            - Called by the Controller to change a track in the loop.
        """
        self.check_position(position)
        if self.loop_tracks[position] is None:
            raise TypeError(f"No tracks are located in position {position}.")
        if params is None:
            self.loop_tracks[position].track_func()
        else:
            self.loop_tracks[position].track_func(params)

    def set_loop_length(self, length: int) -> None:
        """
        Description: Sets a loop's length.
        Args:
            -length(int): The length of the loop, in seconds.
        Returns: None

        Relationships:
            - Sets the length of the loop which is also the longest track.
        """
        if length < 0:
            raise ValueError("Invalid length")
        self.loop_length = max(length, self.loop_length)

    def set_loop_elapsed_secs(self, time) -> None:
        """
        Description: Sets the elapsed time of the loop.
        Args:
            -length(int): The length of the loop, in seconds.
        Returns: None
        """
        self.loop_elapsed_secs = time

    def get_loop_elapsed_secs(self, time) -> int:
        """
        Description: Returns the elapsed time of the loop.
        Args:
            - None
        Returns: elapsed time in seconds
        """
        return self.loop_elapsed_secs

    def get_loop_selection(self) -> bool:
        """
        Description: Returns if loop is selected.
        Args:
            - None
        Returns: boolean
        """
        return self.is_selected

    def toggle_selection(self) -> None:
        """
        Description: Changes boolean to reflect if loop is selected.
        Args:
            - None
        Returns:
            - None
        """
        self.is_selected = not self.is_selected

    def get_loop_id(self) -> str:
        """
        Description: Returns the loop's ID.
        Args:
            - None
        Returns:
            - loop_id (str)
        """
        return self._loop_id

    def update_loop(self):
        """
        TODO
        """
        pass
