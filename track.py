from dataclasses import dataclass
from time import time
from datetime import datetime
import sounddevice as sd
import numpy as np
import soundfile as sf
import os

assert np  # keeps linter from complaining np isn't directly called

DEFAULT_TRACK_NAME = "New Track"


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
        track_name: str = DEFAULT_TRACK_NAME,
        channel_config=1,
        reverse_track=False,
        time_dilation=0,
        pitch_modulation=0,
    ):
        # track attributes
        self.track_name = track_name
        self.track_birth = datetime.now()
        self.track_id = f"Track_{self.track_birth.strftime("%Y%m%d%H%M%S")}"
        self.track_state = "STOP"
        self.track_volume = 1.0
        self.channel_config = channel_config
        self.track_birth = time()  # format is seconds since Unix epoch
        self.track_filepath = self.generate_track_path()

        # effects
        self.is_reversed = reverse_track
        self.time_dilation = time_dilation
        self.pitch_modulation = pitch_modulation

    def __repr__(self):
        name = self.track_name if self.track_name else self.track_id
        filename = getattr(self, 'track_filename', 'None')
        return f"Track(id={self.track_id}, name={name}, .wav file={filename})"

    def generate_track_path(self) -> str:
        """
        Description: Ensures project directories are present then creates a
                     path to the next track audio file.
        Args:
            - None.
        Returns:
            - A string containing the track's file path.
        Relationship(s):
            - None.
        """
        # create file name
        file_name = f"track_{self.track_birth}.wav"

        projects_dir = "projects"  # top level directory
        # add subdirectories to path if not present
        recordings_dir = os.path.join(projects_dir, "recordings")
        waveforms_dir = os.path.join(projects_dir, "waveforms")
        wav_images_dir = os.path.join(projects_dir, "waveform_images")

        # exist_ok=True avoids raising err if directories already exist
        os.makedirs(recordings_dir, exist_ok=True)
        os.makedirs(waveforms_dir, exist_ok=True)
        os.makedirs(wav_images_dir, exist_ok=True)

        return os.path.join(recordings_dir, file_name)

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

    def get_reverse(self):
        """
        Description: Returns if the track is reversed.
        Args:
            - None
        Returns:
            - Boolean
        Relationship(s):
            - None
        """
        return self.reverse_track

    def set_reverse(self, reverse: bool):
        """
        Description: Sets if the track is reversed.
        Args:
            - Boolean value to indicate if the track is reversed.
        Returns:
            - None
        Relationship(s):
            - None
        """

        self.is_reversed = reverse

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
