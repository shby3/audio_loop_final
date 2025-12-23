"""This program records a track for 5 seconds using built-in computer mic.
The file creates a 'project' file, and within, 'recordings', 'waveform', and 'waveform_image' files.
The recording saves as a .wav file within 'recordings' folder.
Adapted from the pyaudio library documentation.
Initial Author: Daniel Kaufman
"""

import wave
import sys
import pyaudio
import os
from datetime import datetime


def main():
    """
    Description: This program records a track using built-in computer mic.
                File is saved as a .wav file in a directory 'recordings'.
    Args:
        - NONE
    Returns:
        - str: Path to recording file
        - Creates new directories they do not already exist:
            'projects', 'recordings', 'waveform', and 'waveform_image'.
    Relationship(s):
        - Is called when 'record' button is pressed.
        Returns recording filepath to a class builder function to hold track information.
    """

    chunk = 1024
    format = pyaudio.paInt16
    channels = 1 if sys.platform == "darwin" else 2
    rate = 48000
    record_seconds = 5

    # filename set
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = "track" + current_datetime + ".wav"

    # new track project, recordings, and waveform directories created if they do not already exist
    project_dir = "audio_loop_projects"
    if not os.path.isdir(project_dir):
        os.mkdir(project_dir)
    os.chdir(project_dir)

    new_dirs = ["waveforms", "waveform_images", "recordings"]
    for dir in new_dirs:
        if not os.path.isdir(dir):
            os.mkdir(dir)
    os.chdir("recordings")

    # The .wav file is recorded and saved in "new_track" directory
    with wave.open(file_name, "wb") as wf:
        p = pyaudio.PyAudio()
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)

        stream = p.open(
            format=format, channels=channels, rate=rate, input=True
        )

        print("Recording...")
        for _ in range(0, rate // chunk * record_seconds):
            wf.writeframes(stream.read(chunk))
        print("Done")

        stream.close()
        p.terminate()

    track_path = os.getcwd() + "/" + file_name
    return track_path


def clean_up():
    """
    Description: This function cleans up files created during testing of the program.
    Args:
        - NONE
    Returns:
        - Deletes new directories and subfiles that were created when main() was called
    Relationship(s):
        - Only used in testing suites.
    """
    os.rmdir("audio_loop_projects")


if __name__ == "__main__":
    main()
