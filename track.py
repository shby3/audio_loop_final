from dataclasses import dataclass
from time import time
from datetime import datetime
import sounddevice as sd
import numpy as np
import soundfile as sf

assert np  # keeps linter from complaining np isn't directly called

RECORD_LENGTH = 10  # in seconds
BPM = 120  # beats per minute
SAMPLE_RATE = 48000  # audio samples per second
SAMPLES_PER_BEAT = (SAMPLE_RATE * 60) / BPM
BEATS_PER_BAR = 4
SAMPLES_PER_BAR = SAMPLES_PER_BEAT * BEATS_PER_BAR  # 4/4 bar

DEFAULT_TRACK_NAME = "New Track"


@dataclass
class Track:
    """
    Description: Represents a single audio layer within a loop.
    Args:
        - track_id (int): A unique track identifier.
        - assigned_loop (Loop obj): The loop of which the given track is
                                    layered within.
        - track_length_secs (int): The length of the track in seconds.
        - track_elapsed_secs (int): Time elapsed during track playback in
                                    seconds.
        - channel_config (int): Mono (1) or stereo (2) setting.
        - reverse_track (bool): Describes whether the track is reversed.
        - TODO: update record_track() to pass sample progress to MasterClock
        - play_track() TODO write this function
        - callback() TODO extract callback function from draft_instant_playback
    """

    def __init__(
        self,
        track_name: str = DEFAULT_TRACK_NAME,
        assigned_loop: object = None,
        track_length_secs=RECORD_LENGTH,
        track_elapsed_secs=0,
        channel_config=1,
        reverse_track=False,
        time_dilation=0,
        pitch_modulation=0,
    ):
        # track attributes
        self.track_name = track_name
        self.track_birth = datetime.now()
        self.track_id = f"Track_{self.track_birth.strftime("%Y%m%d%H%M%S")}"
        self.track_length_secs = track_length_secs  # set by first recording?
        self.track_elapsed_secs = track_elapsed_secs
        self.assigned_loop = assigned_loop
        self.track_state = "STOP"
        self.track_volume = 1.0
        self.channel_config = channel_config
        self.track_birth = time()  # format is seconds since Unix epoch
        self.track_filepath = self.generate_track_path(".wav")
        self.waveform_filepath = self.generate_track_path(".png")

        # recording properties
        self.sample_rate = SAMPLE_RATE
        self.samples_per_beat = SAMPLES_PER_BEAT
        self.dtype = "float32"  # for numpy array holding audio data

        # a common range is 128-1024.
        # lower = less latency but more CPU intensive
        self.blocksize = 256  # number of audio frames processed per callback
        self.samples_per_beat = SAMPLES_PER_BEAT
        self.overdub_track = False
        self.wav_subtype = "PCM_16"  # good compatibility

        # effects
        self.is_reversed = reverse_track
        self.time_dilation = time_dilation
        self.pitch_modulation = pitch_modulation

    def __repr__(self):
        name = self.track_name if self.track_name else self.track_id
        filename = getattr(self, 'track_filename', 'None')
        return f"Track(id={self.track_id}, name={name}, .wav file={filename})"

    def record_track(self):
        """
        Description: Records audio to the track as a .wav file.
        Args:
            - None.
        Returns:
            - None.
        Relationship(s):
            - None.
        # TODO: Method eventually moving to a controller class
        """
        length = self.track_length_secs
        channels = self.channel_config
        samplerate = self.sample_rate
        blocksize = self.blocksize
        dtype = self.dtype
        filepath = self.track_filepath
        wav_subtype = self.wav_subtype
        frames_total = length * samplerate
        frames_written = 0

        self.track_state = "RECORD"
        print(f"Recording audio to {filepath}...")
        with sf.SoundFile(
            filepath, "w", samplerate, channels, wav_subtype
        ) as track_file:
            with sd.InputStream(
                samplerate, blocksize, None, channels, dtype
            ) as input_stream:

                #  passes mic input to input stream and writes to .wav file
                while frames_written < frames_total:
                    frames_pending = frames_total - frames_written
                    frames_chunk = blocksize
                    # handles where last chunk of frames is less than blocksize
                    if frames_pending < frames_chunk:
                        frames_chunk = frames_pending

                    indata, overflowed = input_stream.read(
                        frames_chunk
                    )  # numpy array shape = (frames_chunk, channels)

                    track_file.write(indata)
                    frames_written += frames_chunk

                print(f"FINISHED recording audio to {filepath}.")
                self.track_state = "STOP"

    def play_track(self):
        """
        Description: Plays back audio from the track.
        Args:
            - None.
        Returns:
            - None.
        Relationship(s):
            - None.
        """
        pass

    def callback(self, outdata, frames, length, status):
        """
        Description: Handles processing of audio data within streams.
        Args:
            - None.
        Returns:
            - None.
        Relationship(s):
            - Used with Stream classes in sounddevice.
            Does not change arg names.
        """
        pass

    def generate_track_path(self, extension):
        """
        Description: Generates a unique file path for the track.
        Args:
            - extension (str): The file extension for the track file.
        Returns:
            - file_name (str): The generated file path.
        Relationship(s):
            - Used to generate a unique file path for the track.
        """
        if not hasattr(self, 'track_filename'):
            self.track_filename = f"{self.track_id}{extension}"

        return f"{self.track_id}{extension}"

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
