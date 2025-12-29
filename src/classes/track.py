import copy
from dataclasses import dataclass
from time import time, sleep
from datetime import datetime
import sounddevice as sd
import numpy as np
import soundfile as sf
import os
import re

assert np  # keeps linter from complaining np isn't directly called

DEFAULT_TRACK_NAME = "New Track"
SAMPLE_RATE = 44100
DEFAULT_TRACK_SEC = 4
DEFAULT_TRACK_LEN = SAMPLE_RATE * DEFAULT_TRACK_SEC
DTYPE = 'float32'
EMPTY_TRACK = np.full((DEFAULT_TRACK_LEN, 2), 0, dtype=DTYPE)


@dataclass
class Track:
    """
    Description: Represents a single audio layer within a loop.
    Args:
        - track_id (int): A unique track identifier.
        - channel_config (int): Mono (1) or stereo (2) setting.
        - reverse_track (bool): Describes whether the track is reversed.
    """

    def __init__(
        self,
        track_name=DEFAULT_TRACK_NAME,
        channel_config=2,
        time_dilation=0,
        pitch_modulation=0,
        project_path="..",
        track_filepath=None,
        left=1.0,
        right=1.0
    ):
        # track attributes
        self.track_name = track_name
        self.track_birth = datetime.now()
        self.track_id = f"Track_{self.track_birth.strftime("%Y%m%d%H%M%S")}"
        self.track_volume = 1.0
        self.channel_config = channel_config
        self.project_path = project_path
        self.track_filepath = track_filepath
        self.left = left
        self.right = right

        # Get track data
        if track_filepath is None:
            self.track_data = copy.copy(EMPTY_TRACK)
        else:
            data, self.track_fs = sf.read(track_filepath, always_2d=True)
            if len(data) > DEFAULT_TRACK_LEN:
                self.track_data = data[:DEFAULT_TRACK_LEN]
            else:
                self.track_data = copy.copy(EMPTY_TRACK)
                self.track_data[:len(data)] = data

        # effects
        self.time_dilation = time_dilation
        self.pitch_modulation = pitch_modulation

    def __repr__(self):
        return f"Track(id={self.track_id}, name={self.track_name}, .wav file={self.track_filepath})"

    def generate_track_file(self) -> str:
        """
        Description: Create a track file from track data.

        Args:
            - None.
        Returns:
            - A string containing the track's file path.
        Relationship(s):
            - None.
        """
        # Create directories if necessary
        audio_dir = self.project_path + "/audio"
        os.makedirs(audio_dir, exist_ok=True)
        os.makedirs(self.project_path, exist_ok=True)

        # create file name
        clean_time = re.sub(r'[ :.]+', '-', str(datetime.now()))
        file_name = f"track_{clean_time}.wav"

        # Create a wav file
        filepath = os.path.join(audio_dir, file_name)
        sf.write(filepath, self.track_data, SAMPLE_RATE)
        # Set new filepath for Track
        self.track_filepath = filepath
        return filepath

    def get_volume(self):
        """
        Description: Obtains volume of the track.
        Args:
            - None.
        Returns:
            - Float between 0.0-1.0
        Relationship(s):
            - Used to determine the volume of a track buffer
             during playback
        """
        return self.track_volume

    def set_volume(self, volume: float):
        """
        Description: Obtains volume of the track.
        Args:
            - float between 0.0-1.0
        Returns:
            - Nothing
        Relationship(s):
            - Controller accesses this function to change the volume
            of a track.
        """

        if volume < 0.0 or volume > 1.0:
            Exception("Volume must be between 0.0 and 1.0")
        self.track_volume = volume

    def reverse(self):
        """
        Description: Reverses the audio data of the given track.
        Args:
            - None
        """
        self.track_data = self.track_data[::-1]

    def add_effect(self, effect, key):
        """
        Description: Adds an effect to the track.

        Args:
            - effect (function): for loop to read and apply to track data
            - key (str): key to put in self.effects dictionary
        """
        self.effects[key] = effect

    def get_pitch_modulation(self):
        """
        Description: Returns if the track is pitch-modulated.
        Args:
            - None
        Returns:
            - Integer which indicates half-steps up or down
            (positive or negative integers) the original recording
        Relationship(s):
            - None
        """

        return self.pitch_modulation

    def set_pitch_modulation(self, pitch_modulation: int):
        """
        Description: Sets pitch modulation of the track.
        Args:
            - Integer which indicates half-steps up or down
            (positive or negative integers) the original recording
        Returns:
            - None
        Relationship(s):
            - None
        """
        self.pitch_modulation = pitch_modulation

    def get_time_dilation(self):
        """
        Description: Returns if the track is reversed.
        Args:
            - None.
        Returns:
            - Float value to indicate if the track is time-dilated.
            Values larger than one indicate the time is sped up.
            Values less than 1 indicate the value is slowed-down.
        Relationship(s):
            - None
        """

        return self.time_dilation

    def set_time_dilation(self, time_dilation: float):
        """
        Description: Sets time dilation of the track.
        Args:
            - Float value to indicate if the track is time-dilated.
            Values larger than one indicate the time is sped up.
            Values less than 1 indicate the value is slowed-down.
        Returns:
            - None
        Relationship(s):
            - None
        """

        self.time_dilation = time_dilation

    def get_channel_config(self) -> int:
        """
        Description: Returns the channel configuration.
        Args: None
        Returns: channel configuration (int)
        """
        return self.channel_config

    def get_track_name(self):
        """
        Description: Returns the track name.
        Args: None
        Returns: track name (str)
        """
        return self.track_name

    def set_track_name(self, track_name: str):
        """
        Description: Sets the track name.
        Args:
            - track_name (str): The name to set for the track
        Returns: None
        """
        self.track_name = track_name


if __name__ == "__main__":
    track = Track(track_filepath="../../projects/samples/scale.aif")
    sd.play(track.track_data, SAMPLE_RATE)
    sleep(6)
    print(track)
    print(track.track_filepath)
