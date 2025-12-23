import sounddevice as sd
import numpy as np
import soundfile as sf
import loop


assert np  # keeps linter from complaining np isn't directly called

""""
+++------------------------------------------------------------------------+++
This file contains functions related to audio playback.
+++------------------------------------------------------------------------+++
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
from time import sleep

sample_file = './scale.aif'


if __name__ == '__main__':

    data, fs = sf.read(sample_file, always_2d=True)
    recording_track = np.full((len(data), 2), 0, dtype='float32')

    loop_effects = {
        "is_recording": False
    }

    def callback(indata, outdata, frames, time, status):
        global current_frame

        if status:
            print(status)
        # Chunksize is the number of frames in indata/outdata or the frames
        # remaining in the audio data.
        chunksize = min(len(data) - current_frame, frames)

        end_frame = current_frame + chunksize
        # Output chunksize frames to be processed
        outdata[:chunksize] = data[current_frame:end_frame] + recording_track[current_frame:end_frame]

        # Record to the recording track if recording is on
        if loop_effects["is_recording"]:
            recording_track[current_frame:end_frame] += indata[:chunksize]

        # If the length of audio data was output, output the remaining frames
        # starting and start at the beginning.
        if chunksize < frames:
            end_frame = frames - chunksize
            outdata[chunksize:frames+chunksize] = data[:end_frame] + recording_track[:end_frame]
            current_frame = end_frame
            if loop_effects["is_recording"]:
                recording_track[:end_frame] = indata[chunksize:frames+chunksize]
        else:
            current_frame += chunksize

    current_frame = 0
    stream = sd.Stream(samplerate=fs, callback=callback)

    with stream:
        print("Playing loop")
        sleep(4)
        print("Recording in 4 seconds")
        sleep(1)
        print("3")
        sleep(1)
        print("2")
        sleep(1)
        print("1")
        sleep(1)
        print("Now")
        loop_effects["is_recording"] = True
        sleep(4)
        print("Overdubbing")
        sleep(2)
        loop_effects["is_recording"] = False
        print("Stopping recording (mid loop)")
        sleep(4)
        print("Recording (mid loop)")
        loop_effects["is_recording"] = True
        sleep(8)
        print("Stopping recording")
        loop_effects["is_recording"] = False
        sleep(24)
        print("Stopping playback")
        stream.stop()


if __name__ == "__main__":
    pass
