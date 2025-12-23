from time import time
from datetime import datetime
import sounddevice as sd
import numpy as np
import soundfile as sf
import os

assert np  # keeps linter from complaining np isn't directly called

""""
This basic instant playback program takes three five-second recordings, mixes
them, and plays them back simultaenously.
"""


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
    # TODO: Method eventually moving to a controller class
    """
    # create track file if needed
    if filepath is None:
        filepath = generate_track_path()

    frames_total = max_duration_secs * samplerate
    frames_written = 0
    # TODO: set track state i.e. track.update_state("record")

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

            - TODO: Note: vector operations can be done on numpy ndarrays
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
            # TODO: set track state i.e. track.update_state("play")

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


def play_track_file(
    filepath: str,
    blocksize: int = 256,
    device: int = None,
    d_type: str = "float32",
):
    """
    Description: Plays audio track from its .wav file.
    Args:
        - filepath: (str) - Relative path to the new track file.
        - device (int) - Refers to the computer's external output devices i.e.
                         speaker. Can view with call to sd.query_devices()
        - blocksize: (int) - Number of audio frames processed per callback.
        - d_type: (str) - Numpy array data type.
    Returns:
        - None.
        Relationship(s):
        - filepath passed taken from generate_track_path() call.
    # TODO: Method eventually moving to a controller class
    """
    # open file
    with sf.SoundFile(filepath, "r") as track_file:
        samplerate = track_file.samplerate
        channels = track_file.channels

        # define callback func for audio processing
        def callback(outdata, frames, time, status):
            if status:
                # TODO: remove debugging print statement from callback later
                print(status)

            audio_data = track_file.read(frames, dtype=d_type, always_2d=True)

            # handle EOF - backfills dead air
            audio_length = len(audio_data)
            if len(audio_data) < len(outdata):
                outdata[:audio_length] = audio_data
                outdata[audio_length:] = 0
                raise sd.CallbackStop()
            else:
                outdata[:] = audio_data

        # set up output stream for playback
        with sd.OutputStream(
            samplerate=samplerate,
            channels=channels,
            blocksize=blocksize,
            device=device,
            dtype=d_type,
            callback=callback,
        ):
            # Keep process alive until callback finished
            sd.sleep(int((len(track_file) / samplerate) * 1000))


def play_track_buffer(
    track_buffer: np.ndarray,
    samplerate: int = 48000,
    channels=None,
    blocksize: int = 256,
    device=None,
    dtype: str = "float32",
):
    """
    Description: Plays a track from an audio buffer.
    Args:
        - track_buffer (numpy ndarray): Track's audio data.
                                        Shape = (frames, channels)
        - samplerate: (int) - How many samples are taken per second i.e.
                              48000kHz = 48000 samples/second
        - channels (int): Channel configuration. 1 = Mono, 2 = Stereo
        - blocksize (int): Number of audio frames to process per callback
        - device (int | None): External device to output audio to (i.e.
          speaker)
        - dtype (str): Numpy array data type.
    Returns:
        - track_buffer (numpy ndarray): Track's audio data.
                                        Shape = (frames, channels)
    Relationship(s):
        - None.
    """
    buffer_idx = 0

    def callback(outdata, frames, time, status):
        nonlocal buffer_idx
        snippet_start_idx = buffer_idx
        snippet_end_idx = snippet_start_idx + frames
        snippet_buffer = track_buffer[snippet_start_idx:snippet_end_idx].copy()

        #  backfills dead air
        snippet_buffer_length = len(snippet_buffer)
        if snippet_buffer_length < frames:
            outdata[:snippet_buffer_length] = snippet_buffer[:]
            outdata[snippet_buffer_length:] = 0
            raise sd.CallbackStop()
        else:
            outdata[:] = snippet_buffer

        buffer_idx += frames

        # print(f"Buffer index = {buffer_idx}") # debug

    with sd.OutputStream(
        samplerate, blocksize, device, channels, dtype, callback=callback
    ):
        # give playback time to finish
        sd.sleep(
            (int(len(track_buffer) / samplerate) * 1000) + 1
        )  # TODO: confirm if +1 is needed for padding, or will cause issues

    print(f"Length of track buffer = {len(track_buffer)}")
    return track_buffer


def mix_track_buffers(track_buffers: list):
    """
    Description: Takes a list of track buffers and mixes them into a single
                 mixed buffer.
    Args:
        - track_buffers (list[numpy ndarrays]): A collection of individual
                                                track buffers.
    Returns:
        - mixed_buffer (numpy ndarray): a buffer containing the mixed audio
                                        samples for the given tracks.
    Relationship(s):
        - Can be passed to play_track_buffer() for playback.
    """

    max_track_length = 0
    max_channels = 1
    # find longest track and max channels
    for buffer in track_buffers:
        max_track_length = max(buffer.shape[0], max_track_length)
        if buffer.ndim > 1:
            max_channels = max(buffer.shape[1], max_channels)

    # add padding to mono tracks, or tracks shorter than the longest
    buffers_to_pad = []
    for buffer in track_buffers:
        if buffer.ndim == 1:
            buffer = buffer.reshape(-1, 1)  # turns mono into stereo
        if buffer.shape[1] < max_channels:
            # tile creates a new array by repeating the given array x times
            buffer = np.tile(buffer, (1, max_channels))
        padding = np.zeros(
            (max_track_length - len(buffer), max_channels), dtype=np.float32
        )
        # vstack combines the arrays vertically aka by adding rows
        buffers_to_pad.append(np.vstack((buffer, padding)))

    mixed_buffer = np.sum(track_buffers, axis=0)

    # normalize to avoid audio clipping
    max_amplitude = np.max(np.abs(mixed_buffer))
    if max_amplitude > 1.0:
        mixed_buffer /= max_amplitude

    return mixed_buffer


if __name__ == "__main__":
    recording_length_secs = 5
    num_channels = 1  # mono
    sample_rate = 48000  # kHz
    blocksize = 256
    d_type = "float32"  # numpy data type
    new_wav_subtype = "PCM_16"  # 16-bit

    track_buffers = []
    track_count = 1
    for track in range(0, 3):
        print("-+-" * 10)
        print(f"Preparing to record Track # {track_count}")
        track_path = generate_track_path()
        path, buffer = record_track(
            recording_length_secs, track_path, channels=num_channels
        )
        track_buffers.append(buffer)
        track_count += 1

    mixed_buffer = mix_track_buffers(track_buffers)
    print("Playing mixed buffer...")
    play_buffer = play_track_buffer(mixed_buffer)
    print("Playback finished!")

    play_track_file(track_path, blocksize)
    print("-+-" * 10)
    print(f"Record Buffer: {buffer}")
    print()
    print()
    print(f"Play Buffer: {play_buffer}")
    print("-+-" * 10)
