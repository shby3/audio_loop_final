from time import time
from datetime import datetime
import sounddevice as sd
import numpy as np
import soundfile as sf
import os
import heapq as min_heap

assert np  # keeps linter from complaining np isn't directly called


RECORD_LENGTH = 10  # in seconds
BPM = 120  # beats per minute
SAMPLE_RATE = 48000  # audio samples per second
SAMPLES_PER_BEAT = (SAMPLE_RATE * 60) / BPM
BEATS_PER_BAR = 4
SAMPLES_PER_BAR = SAMPLES_PER_BEAT * BEATS_PER_BAR  # 4/4 bar


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
    """

    def __init__(
        self,
        track_id: int,
        assigned_loop: object,
        track_length_secs=RECORD_LENGTH,
        track_elapsed_secs=0,
        channel_config=1,
        reverse_track=False,
    ):
        # track attributes
        self.track_id = track_id
        self.track_length_secs = track_length_secs  # set by first recording?
        self.track_elapsed_secs = track_elapsed_secs
        self.assigned_loop = assigned_loop
        self.track_state = "STOP"
        self.track_volume = 1.0
        self.channel_config = channel_config
        self.track_birth = time()  # format is seconds since Unix epoch
        self.track_filepath = self.generate_track_path()

        # recording properties
        self.sample_rate = SAMPLE_RATE
        self.samples_per_beat = SAMPLES_PER_BEAT
        self.dtype = "float32"  # for numpy array holding audio data

        # common range is 128-1024. lower = less latency but more CPU intensive
        self.blocksize = 256  # number of audio frames processed per callback
        self.samples_per_beat = SAMPLES_PER_BEAT
        self.overdub_track = False
        self.wav_subtype = "PCM_16"  # good compatibility

        # effects
        self.reverse_track = reverse_track

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
            - Used with Stream classes in sounddevice. Do not change arg
              names.
        """
        pass

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


class Loop:
    """
    Description: represents a collection of layered audio files (aka tracks).

    Args:
        - loop_id (int): unique identifier for the loop.
        - loop_length_secs (int): Loop duration in seconds.
        - loop_elapsed_secs (int): Time elapsed in loop, in seconds.
        - loop_tracks (dict): Keys = Track numbers, Values = Track objects
    """

    def __init__(
        self,
        loop_id,
        loop_length_secs=RECORD_LENGTH,
        loop_elapsed_secs=0,
        loop_tracks=None,
    ):
        self.loop_tracks = {}  # keys = track num, vals = Track obj
        if loop_tracks is not None:
            self.loop_tracks = loop_tracks

        self.loop_id = loop_id
        self.num_tracks = 0  # number of tracks in the loop
        self.loop_length_secs = loop_length_secs
        self.loop_elapsed_secs = loop_elapsed_secs
        self.loop_state = "STOP"  # TODO: state isn't implemented yet
        self.loop_birth = time()  # format is seconds since Unix epoch

        # TODO: track creation eventually moving to controller class
        self.add_track()

    def add_track(self):
        """
        Description: Adds a track to the loop.

        Args:
            - None.
        Returns:
            - None.
        Relationship(s):
            - None.
        """
        self.num_tracks += 1
        self.loop_tracks[self.num_tracks] = Track(self.num_tracks, self)

    def get_track(self, track_num: int):
        """
        Description: Returns a given Track object with its track number.
        Args:
            - track_num (int): The track's position within the loop i.e. 1.
        Returns:
            - The referenced Track object.
        Relationship(s):
            - None.
        """
        return self.loop_tracks[track_num]


class TrackScheduler:
    """
    Description: Directs the execution of audio transport activities (play,
                 pause, stop, record, etc.)
    Args:
        - clock (MasterClock obj): "Time keeper" of the scheduler that
                                    synchronizes by sample.
    Relationship(s):
        - None. TODO: Add relationships once finalized.
    """

    def __init__(self, clock):
        self.clock = clock  # master clock
        self.event_queue = []
        self.next_event = None
        self.next_event_due_sample = None
        self.total_events_created = 0

    def add_event(self, event: object) -> None:
        """
        Description: Adds an event to the queue.
        Args:
            - event (Event obj): The audio event being added.
        Returns:
            - None.
        Relationship(s):
            - None.
        """
        min_heap.heappush(self.event_queue, event)
        self.update_next_event()
        self.total_events_created += 1

    def update_next_event(self) -> None:
        """
        Description: Updates which event is next in the queue.
        Args:
            - None.
        Returns:
            - None.
        Relationship(s):
            - updates self.next_event property
        """
        if len(self.event_queue) > 0:
            self.next_event = self.event_queue[0]
            self.next_event_due_sample = self.next_event.get_due_sample()

        else:
            self.next_event = None
            self.next_event_due_sample = None

    def get_next_event(self) -> object:
        """
        Description: Returns the next event in the queue.
        Args:
            - None.
        Returns:
            - next_event (Event obj): the next event in the queue.
        Relationship(s):
            - None.
        """
        return self.next_event

    def get_next_event_due_sample(self):
        """
        Description:
        Args:
            - param1 (Type):
            - param2 (Type):
        Returns:
            -
        Relationship(s):
            -
        """
        return self.next_event_due_sample

    def empty_queue(self):
        """
        Description: Empties the queue and prints its contents.
        Args:
            - None.
        Returns:
            - events (list[tuple(event_due_sample, event_id)]): the
        Relationship(s):
            - Primarily used for testing.
        """
        events = []
        while self.event_queue:
            event = min_heap.heappop(self.event_queue)
            events.append((event.get_due_sample(), event.get_id()))
        print(events)
        return events


class Event:
    """
    Description: represents an audio transport event (play, pause, stop,
                 record, etc.)
    Args:
        - event_id (int): unique identifier for the event.
        - event_track (Track obj): track associated with the event.
        - event_loop (Loop obj): loop associated with the event.
        - event_action (func): transport action (play, pause, stop, record,
                               etc.) triggered by the event.
        - event_due_sample (int): what sample index the event is due to
                                  trigger.

    Relationship(s):
        - Used by TaskScheduler to queue transport activities (play, pause,
          stop, record, etc.).
    """

    def __init__(
        self,
        event_id: int,
        event_track: Track,
        event_loop: Loop,
        event_action: callable,
        event_due_sample: int,
    ):
        self.event_id = event_id
        self.event_track = event_track
        self.event_loop = event_loop
        self.event_action = event_action
        self.event_due_sample = event_due_sample

    def get_id(self) -> int:
        """
        Description: returns an event's id number.
        Args:
            - None.
        Returns:
            - event_id (int): unique event identifier.
        Relationship(s):
            - None.
        """
        return self.event_id

    def get_track(self):
        """
        Description: returns an event's associated track.
        Args:
            - None.
        Returns:
            - event_track (Track obj): event's Track.
        Relationship(s):
            - None.
        """
        return self.event_track

    def get_loop(self):
        """
        Description: returns the loop an event belongs to..
        Args:
            - None.
        Returns:
            - assigned_loop (Loop obj): the event's loop.
        Relationship(s):
            - None.
        """
        return self.event_loop

    def get_action(self):
        """
        Description: returns an event's id executable action.
        Args:
            - None.
        Returns:
            - The event's action.
        Relationship(s):
            - None.

        TODO: Determine how action methods will be passed.
        """

        return self.event_action

    def get_due_sample(self):
        """
        Description: returns the sample index where the event should begin.
        Args:
            - None.
        Returns:
            - event_due_sample (int)
        Relationship(s):
            - None.
        """
        return self.event_due_sample

    def __lt__(self, some_other_event: object) -> bool:
        """
        Description: Magic method that sets event_due_sample as the property
                     to reference when comparing Event objects. In the event
                     of a tie, event_id is used.
        Args:
            - some_other_event (Event): A different Event object.
        Returns:
            - True if this event's due_sample is less than the other event's
              due_sample.
        Relationship(s):
            - Necessary for min heap comparisons in TaskScheduler.
        """
        if self.event_due_sample > some_other_event.get_due_sample():
            return False

        elif self.event_due_sample < some_other_event.get_due_sample():
            return True

        elif self.event_id < some_other_event.get_id():
            return True

        return False


class AppController:
    def __init__(self):
        self.loop_num = 0

    def spawn_loop(self):
        pass


class MasterClock:
    """
    Description: The central timekeeping reference used by TrackScheduler to
    sync transport events (play, pause, stop, record, etc.) to quantized
    sample indexes.
    Args:
        - sample_rate (int): the number of audio samples taken per second.
        - bpm (int): The tempo of the track
        - time_signature (tuple[int, int]: the time signature of the track
        - note_subdivision (float): the way a musical beat is divided into
                                    smaller, evenly spaced rhythmic units.
                                    For example a quarter note would be (1/4)
                                    = 0.25.
        - current_sample_index (int): The index of the current sample being
                                      transmitted in the loop .
    Returns:
        -
    Relationship(s):
        - Used by TrackScheduller to synchronize transport events (play, stop,
          record, etc.) by sample.
    """

    def __init__(
        self,
        sample_rate: int,
        bpm: int,
        time_signature: tuple[int, int],
        note_subdivision: float,
        current_sample_index: int = 0,
    ):
        self.sample_rate = sample_rate
        self.bpm = bpm
        self.samples_per_beat = self.get_samples_per_beat()
        self.beats_per_sample = 1 / self.samples_per_beat
        self.time_signature = time_signature
        self.beats_per_bar = self.get_beats_per_bar()
        self.samples_per_bar = self.get_samples_per_bar()
        self.note_subdivision = note_subdivision
        self.samples_per_tick = self.get_samples_per_tick()
        self.current_sample_index = current_sample_index

    def get_samples_per_beat(self):
        """Description: returns samples per beat."""
        return (self.sample_rate * 60) / self.bpm

    def get_beats_per_bar(self):
        """Description: returns beats per bar."""
        return self.time_signature[0] * (4 / self.time_signature[1])

    def get_samples_per_bar(self) -> int:
        """Description: returns samples per bar."""
        return int(round(self.samples_per_beat * self.beats_per_bar))

    def get_samples_per_tick(self) -> int:
        """Description: returns samples per tick."""
        samples_per_tick = int(
            round(self.samples_per_beat * self.note_subdivision)
        )
        # minimum 1 sample per tick
        if samples_per_tick < 1:
            samples_per_tick = 1
        return samples_per_tick

    def increment_sample_index(self, num_frames: int) -> None:
        """
        Description: Increments the current sample index by the number of
                     frames processed.
        """
        self.current_sample_index += num_frames

    def get_closest_snap_point(self, sample_index: int) -> int:
        """
        Description: Returns the index of the closest sample to snap a
                     transport event (play, pause, stop, record, etc.) to via
                     quantization.
        Args:
            - sample_index (int) the index of the given sample.
        Returns:
            - The adjusted sample index where the transport event should take
              place.
        """
        return (
            # instead of round(): avoids float rounding errors
            (int(sample_index) + self.samples_per_tick // 2)
            // self.samples_per_tick
        ) * self.samples_per_tick

    def event_executed():
        """
        Description: tester function to pass to events. Prints a message to
                     the terminal.
        """
        print("Event executed.")


if __name__ == "__main__":
    sample_rate = 48000
    bpm = 120
    time_sig = (1, 4)
    note = 1 / 4
    current_sample_index = 21000
    clock = MasterClock(sample_rate, bpm, time_sig, note, current_sample_index)

    # Example test events for queue testing
    e1 = Event(
        event_id=1,
        event_track="drums",
        event_loop=0,
        event_action=lambda: print("Kick triggered"),
        event_due_sample=24000,
    )

    e7 = Event(
        event_id=2,
        event_track="drums",
        event_loop=0,
        event_action=lambda: print("Snare triggered"),
        event_due_sample=36000,
    )

    e3 = Event(
        event_id=3,
        event_track="bass",
        event_loop=0,
        event_action=lambda: print("Bass note A"),
        event_due_sample=48000,
    )

    e4 = Event(
        event_id=4,
        event_track="synth",
        event_loop=0,
        event_action=lambda: print("Synth chord"),
        event_due_sample=96000,
    )

    e5 = Event(
        event_id=5,
        event_track="vocals",
        event_loop=1,
        event_action=lambda: print("Vocal sample triggered"),
        event_due_sample=120000,  # start of next bar
    )

    e6 = Event(
        event_id=6,
        event_track="fx",
        event_loop=1,
        event_action=lambda: print("FX whoosh"),
        event_due_sample=60000,  # mid-bar
    )

    e2 = Event(
        event_id=7,
        event_track="claps",
        event_loop=1,
        event_action=lambda: print("clip clap"),
        event_due_sample=60000,  # mid-bar
    )

    events = [e1, e2, e3, e4, e5, e6, e7]
    scheduler = TrackScheduler(clock)

    for event in events:
        scheduler.add_event(event)

    # prints queue to terminal List of (sample index, event ID)
    scheduler.empty_queue()


loop = Loop(1)
track = loop.get_track(1)
# track.record_track()
