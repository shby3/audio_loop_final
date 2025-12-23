from time import time
from datetime import datetime
import sounddevice as sd
import numpy as np
import soundfile as sf
import os

assert np  # keeps linter from complaining np isn't directly called

""""
+++------------------------------------------------------------------------+++
This file contains functions related to audio recording.
+++------------------------------------------------------------------------+++
"""

# defines public modules for importing between directories
__all__ = ["generate_track_path", "record_track", "merge_track_buffers"]


def generate_track_path() -> str:
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
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"track_{current_datetime}.wav"

    projects_dir = "projects"  # top level directory
    # add sub directories to path if not present
    recordings_dir = os.path.join(projects_dir, "recordings")
    waveforms_dir = os.path.join(projects_dir, "waveforms")
    wav_images_dir = os.path.join(projects_dir, "waveform_images")

    # exist_ok=True avoids raising err if directories already exist
    os.makedirs(recordings_dir, exist_ok=True)
    os.makedirs(waveforms_dir, exist_ok=True)
    os.makedirs(wav_images_dir, exist_ok=True)

    return os.path.join(recordings_dir, file_name)


def record_track(
    max_duration_secs: int,
    filepath: str = None,
    dtype: str = "float32",
    wav_subtype: str = "PCM_16",
    channels=1,
    samplerate: int = 48000,
    blocksize: int = 256,
) -> tuple[int, np.ndarray]:
    """
    Description: Records audio to the track as a .wav file.
    Args:
        - max_duration_secs: (int) - recording length in seconds.
        - channels: (int) - Number of channels, 1 = Mono, 2 = Stereo
        - samplerate: (int) - How many samples are taken per second i.e.
                              48000kHz = 48000 samples/second
        - blocksize: (int) - Number of audio frames processed per callback.
        - dtype: (str) - Numpy array data type.
        - filepath: (str) - Relative path to the new track file.
        - wav_subtype: (str) - wav recording format i.e. PCM_16
    Returns:
        - Tuple containing:
            - filepath (str) - path to the audio file created.
            - track_buffer (numpy ndarray with shape (frames, channels))
    Relationship(s):
        - None.
    """
    # create track file if needed
    if filepath is None:
        filepath = generate_track_path()

    frames_total = max_duration_secs * samplerate
    frames_written = 0

    snippet_buffers = []  # stores buffers for each chunk of track audio

    def callback(indata, outdata, frames, time, status):
        """
        Description:  custom function to consume, process or generate audio
                      data in response to requests from an active stream.
        Args:
            - indata (numpy ndarray): Stores a block of incoming audio samples
                                      (aka snippet buffers) from the mic.
                                      - Shape = (frames, channels)
                                      - Prefilled before PortAudio (via
                                        sounddevice) calls this function.
                                      - can be read but not  modified
                                        directly.
            - outdata (numpy ndarray): Stores a block of outgoing audio
                                       samples (aka snippets) to the speaker.
                                     - Shape = (frames, channels)
                                     - initialized with garbage values, must
                                       be filled to hold real data.
            - frames (int): The number of frames (which is samples per
                            channel) is in this audio snippet buffer.
                            - will generally be blocksize until the last
                              block.
            - time (obj):  Holds high-precision timing data from PortAudio.
                           - time.inputBufferAdcTime (float): time when the
                             first sample in the current indata block was
                             recorded by the ADC, in seconds. Only relevant
                             for input streams.
                           - time.currentTime (float): time when the callback
                             was invoked, in seconds.
                           -time.outputBufferDacTime (float): time when the
                            first sample in the outdata buffer will reach the
                            DAC, in seconds. Only relevant for output streams.
            - status (StreamStatus obj): reports runtime warnings, buffer
                                         problems, or data flow issues that
                                         occurred between the audio driver and
                                         the callback. Behaves like a set of
                                         flags.
        Returns:
            - None.
        Relationship(s):
            - Passed to a sounddevice stream instance
        """
        #  sounddevice np array buffers are reused so must be copied to share
        #  outside callback function
        snippet_buffers.append(indata.copy())
        outdata[:] = indata

    print(f"Recording audio to {filepath}...")
    start_time_secs = time()
    with sf.SoundFile(
        filepath, "w", samplerate, channels, wav_subtype
    ) as track_file:
        with sd.InputStream(
            samplerate, blocksize, None, channels, dtype
        ) as input_stream:

            #  passes mic input to input stream and writes to wav file
            while frames_written < frames_total:
                frames_pending = frames_total - frames_written
                frames_chunk = blocksize
                # handles where last chunk of frames is less than blocksize
                if frames_pending < frames_chunk:
                    frames_chunk = frames_pending

                indata, overflowed = input_stream.read(
                    frames_chunk
                )  # numpy array shape = (frames_chunk, channels)
                snippet_buffers.append(indata.copy())
                track_file.write(indata)
                frames_written += frames_chunk

            end_time_secs = time()
            elapsed_time_secs = end_time_secs - start_time_secs
            print(f"FINISHED recording audio to {filepath}.")
            print(f"--> Duration was {elapsed_time_secs}.")

    track_buffer = merge_track_buffers(snippet_buffers)
    return (filepath, track_buffer)


def merge_track_buffers(track_snippets: list) -> np.ndarray:
    """
    Description: Takes a list of an audio track's snippet buffers and combines
                 them into a single track buffer.
    Args:
        - track_snippets (list): A list of a track's snippet buffers.
    Returns:
        - combined_track_buffer (numpy ndarray): The track's full audio buffer
    Relationship(s):
        - Called within play_track_buffer() to combine the buffers for each
          processed audio snippet.
    """
    combined_track_buffer = np.concatenate(track_snippets, axis=0)
    return combined_track_buffer


if __name__ == "__main__":
    pass
