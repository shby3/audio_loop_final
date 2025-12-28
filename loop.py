from datetime import datetime
import os
from track import Track
import numpy as np
import sounddevice as sd
from time import sleep

DEFAULT_LOOP_NAME = "New Loop"
VALID_POSITIONS = [x for x in range(1, 7)]
SAMPLE_RATE = 44100
DEFAULT_LOOP_SEC = 4
DEFAULT_LOOP_LEN = SAMPLE_RATE * DEFAULT_LOOP_SEC


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
        - loop_elapsed_secs (int): The elapsed time of the loop
            (the longest track).
        - loop_birth(str): The birth of the loop, in epochs.

    Methods:
        - check_position(int): Checks if the given position is valid.
        - get_track_list(): Gets a list of Track objects in the loop.
        - get_loop_display_name(): Returns the display name of the loop.
        - set_loop_display_name(str): Sets the display name of the loop.
        - set_track(obj, int): Sets  track at the given position in the loop.
        dictionary of tracks.
        - remove_track(int): Removes a track at specified position
        - move_track(int, int): Move a track to specified position
        - alter_track(func):
        Uses a Track method to alter a Track in the Loop.
        - get_loop_selection(bool): Returns if loop is currently selected.
        - toggle_selection(): Toggles selection.
        - get_loop_id(): Returns the ID of the loop currently selected.

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
        self.loop_id = f"Loop_{self.loop_birth.strftime("%Y%m%d%H%M%S")}"
        self.loop_name = loop_name
        self.current_frame = 0
        self.is_recording = False
        self.is_playing = False
        self.recording_track = 1

        if loop_tracks is None:
            self.loop_tracks = {
                1: Track(track_name="Track 1"),
                2: Track(track_name="Track 2"),
                3: Track(track_name="Track 3"),
                4: Track(track_name="Track 4"),
                5: Track(track_name="Track 5"),
                6: Track(track_name="Track 6"),
            }
        else:
            self.loop_tracks = loop_tracks

        self.stream = sd.Stream(samplerate=SAMPLE_RATE, callback=self._callback)

    def __repr__(self):
        lines = [f"Loop ID: {self.loop_id}", f"Name: {self.loop_name}"]
        for pos in range(1, 7):
            track = self.loop_tracks[pos]
            lines.append(f"Track {pos}: {track if track else 'Empty'}")
        return "\n".join(lines)

    def _callback(self, indata, outdata, frames, time, status):
        if status:
            print(status)
        # Chunksize is the number of frames in indata/outdata or the frames
        # remaining in the audio data.
        chunksize = min(DEFAULT_LOOP_LEN - self.current_frame, frames)

        end_frame = self.current_frame + chunksize
        # Output chunksize frames to be processed, limiting the values to avoid audio clipping
        out = sum(
            track.track_data[self.current_frame:end_frame] for track in self.loop_tracks.values()
        )
        outdata[:chunksize] = np.clip(out, -1.0, 1.0)

        # Record to the recording track if recording is on
        if self.is_recording:
            self.loop_tracks[self.recording_track].track_data[self.current_frame:end_frame] += indata[:chunksize]

        # If the length of audio data was output, output the remaining frames
        # starting and start at the beginning.
        if chunksize < frames:
            end_frame = frames - chunksize
            out = sum(
                track.track_data[:end_frame] for track in self.loop_tracks.values()
            )
            outdata[chunksize:] = np.clip(out, -1.0, 1.0)
            self.current_frame = end_frame
            if self.is_recording:
                self.loop_tracks[self.recording_track].track_data[:end_frame] += indata[chunksize:frames+chunksize]
        else:
            self.current_frame += chunksize

    def play(self):
        """
        Description: Starts playing the audio of tracks in Loop with a sd Stream.
        Args:
                - None
        Returns:
                - None
        """
        self.stream.start()
        self.is_playing = True

    def stop(self):
        """
        Description: Stops playing the audio of tracks in Loop with a sd Stream, and
        sets self.current_frame to zero.
        Args:
                - None
        Returns:
                - None
        """
        self.stream.stop()
        self.is_playing = False
        self.current_frame = 0

    def pause(self):
        """
        Description: Stops playing the audio of tracks in Loop with a sd Stream.
        Args:
                - None
        Returns:
                - None
        """
        self.stream.stop()

    def set_is_recording(self, is_recording):
        """
        Description: Sets is_recording to True or False.
        Args:
                - is_recording: bool
        Returns:
                - None
        """
        self.is_recording = is_recording

    def set_recording_track(self, track):
        """
        Description: Sets the track to record to.

        Args:
            - track: int (1-6)

        Returns:
            - None
        """
        self.recording_track = track

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

    def get_track(self, position: int) -> Track:
        """
        Description: Gets the track at the given position in the loop's
        dictionary of tracks.
        Args:
            position: The position to set the track
        Returns: The track at the given position in the loop.

        Relationships:
            - Called by the Controller to set a track in the loop.
        """
        return self.loop_tracks[position]

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

    def get_loop_id(self) -> str:
        """
        Description: Returns the loop's ID.
        Args:
            - None
        Returns:
            - loop_id (str)
        """
        return self.loop_id


if __name__ == "__main__":
    print("")
    # tracks = {
    #     1: Track(track_name="Track 1"),
    #     2: Track(track_name="Track 2", track_filepath="./projects/samples/kick.aif"),
    #     3: Track(track_name="Track 3", track_filepath="./projects/samples/snare.aif"),
    #     4: Track(track_name="Track 4", track_filepath="./projects/samples/scale.aif"),
    #     5: Track(track_name="Track 5"),
    #     6: Track(track_name="Track 6")
    # }
    # loop = Loop(loop_tracks=tracks)
    # loop.is_recording = True
    # loop.play()
    # sleep(2)
    # loop.stop()
    # sleep(1)
    # loop.play()
    # sleep(2)

