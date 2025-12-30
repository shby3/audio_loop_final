import re
from datetime import datetime

from .file_manager import FileManager
from .loop import Loop
import os

DEFAULT_LOOP_NAME = "New_Loop"
LOOP_DIR = "../projects/loops"


class Controller:
    """
    Description: Controls functions for Loops and Tracks.

    Args:

    Components:
        - Loop: The Loop to be controlled.
        - File Manager: Responsible for serialization / deserialization of loop
                                    and track items.
        - Content List: The file structure associated with storing items in-
                                    memory.
        - GUI: the graphic user interface of the controller, manages input
                                    devices
        - Validator: the validation service the controller uses to determine
                                    if GUI directives are valid before
                                    execution.

    Methods:
        - get_loop(): Returns the current Loop associated with the controller.
        - set_loop(): Sets a new Loop to the Controller
        - serialize_loop (obj: Loop): Takes active loop object mapping and
                                    saves it to .loop file.
        - deserialize_loop (obj: Loop): Takes a .loop file and reads it, stores
                                    it in temp memory for future use.
        - process_filename(): Takes datetime of file creation and manipulates
                                    it so that we have a unique filename for
                                    file creation.
        - load_object (obj_file_name, location): Takes a loop object and
                                    populates GUI with mapped loop data.
        - update_loop (obj: Loop): Takes active loop object and ensures data
                                    maps properly. Loads audio data to buffer
                                    to ensure immediate playback of changes is
                                    available.
        - create_new_loop(): Two-step process of updating active loop, and
                                    creating a new, blank loop object.
        - export_loop_to_track(): Takes a loop object, as if it were going to
                                    play the file, grabs the numpy file path
                                    and processes it into a new Track object.
        - serialize_track (obj: Track) Takes an active track object and saves
                                    it to a .track file.
        - deserialize_track (obj: Track) Takes a .track file and reads it,
                                    stores it in temporary memory for future
                                    use.
        - play_loop: Plays the loop currently in the loop design
                                    area. Initiates a clock to return time
                                    since play was clicked for future pause.
        - pause_loop : Pauses the loop currently in the loop design area.
        - stop_loop (active_loop): Stops the loop currently in the loop design
                                    area. Stop restarts the loop from the first
                                    item in the numpy array.
        - mute_loop (active_loop): Mutes the audio output of the loop currently
                                    in the loop design area. Does not pause or
                                    stop the internal clock associated with
                                    playback.
        - un-mute_loop (active_loop): Un-mutes the audio output of the loop
                                    currently in the loop design area. Does not
                                    pause or stop the internal clock associated
                                    with playback.
        - record_track (active_loop, track_num, channel_config): Uses audio
                                    recorder and audio processor to create an
                                    audio track / audio file recording and
                                    place said file / track into our active
                                    loop.
        - adjust_track_volume (position, volume): Adjusts the volume level
                                    for a track at the specified position.
        - clear_track (position): Removes the track at the specified position
                                    from the active loop.
        - apply_reverse (position): Toggles the reverse effect on the track
                                    at the specified position.
        - apply_xf1 (position, value): Applies XF1 time dilation effect to
                                    the track at the specified position.
        - apply_xf2 (position, value): Applies XF2 pitch modulation effect
                                    to the track at the specified position.
        - solo_track (position): Sets the track at the specified position
                                    for solo playback.
        - apply_mix (position, balance): Applies left/right stereo balance
                                    to the track at the specified position.
        - record_track (position): One-click record button workflow
        - play_button(): One-click play button for loop_to_play
        - pause_button(): One-click pause button
        - stop_button(): One-click stop button
        - save_current_loop(): Save active loop with auto-filename
        - load_loop_from_file (file_path): Complete loop loading workflow
        - new_loop_button(): Create new blank loop
        - export_loop_as_track(): Export loop as single track file
    """
    def __init__(self):
        """
        Initializes an audio loop station controller.
        """
        # Default channel config
        self.no_tracks = 1

        # The loop object we're currently editing.
        self.loop = None

        # Components:
        self.validator = None
        self.gui = None
        self.file_manager = FileManager()
        self.content_list = None

        # Specific mode toggles - changes to specific modes:
        self.load_state = False     # Next drag is obj -> pos
        self.move_state = False     # Next drag is internal pos -> pos.

        # Sets home directory (default to current file's directory)
        self.home_folder = os.path.dirname(__file__)

    # ## ==========================================## #
    # ## --- COMPONENT GETTER / SETTER METHODS --- ## #
    # ## ==========================================## #

    def get_validator(self):
        """
        Description: Returns current validator with settings.
        Args:
            - None.
        Returns:
            - Validator (obj): The Validator object.
        Relationship(s):
            - Used for validating specific actions before actions take place.
        """
        return self.validator

    def set_validator(self, validator):
        """
        Description: Attaches a validator with settings.
        Args:
            - validator (obj): A validator class object.
        Returns:
            - None.
            - [Action]: Patches the validator to the controller.
        Relationship(s):
            - Used for function / method validation before action takes place.
        """
        self.validator = validator

    def get_gui(self):
        """
        Description: Returns current GUI with settings.
        Args:
            - None.
        Returns:
            - gui (obj): The GUI object.
        Relationship(s):
            - All button, gesture, and user-interface for the application.
        """
        return self.gui

    def set_gui(self, gui):
        """
        Description: Attaches a new GUI with settings.
        Args:
            - gui (obj): A GUI class object.
        Returns:
            - None.
            - [Action]: Patches the GUI to the controller.
        Relationship(s):
            - All button, gesture, and user-interface for the application.
        """
        self.gui = gui

    def get_file_manager(self):
        """
        Description: Returns current file manager with settings.
        Args:
            - None.
        Returns:
            - file_manager (obj): The File Manager object.
        Relationship(s):
            - All CRUD operations and serialization / deserialization processes
        """
        return self.file_manager

    def set_file_manager(self, file_manager):
        """
        Description: Attaches a new File Manager with settings.
        Args:
            - file_manager (obj): A File Manager class object.
        Returns:
            - None.
            - [Action]: Patches the File Manager to the controller.
        Relationship(s):
            - All CRUD operations and serialization / deserialization processes
        """
        self.file_manager = file_manager

    def get_content_list(self):
        """
        Description: Returns current content list with settings.
        Args:
            - None.
        Returns:
            - content_list (obj): The Content List object.
        Relationship(s):
            - All .loop / .track items associated with controller
        """
        return self.content_list

    def set_content_list(self, content_list):
        """
        Description: Attaches a new Content List with settings.
        Args:
            - content_list (obj): A Content_List class object.
        Returns:
            - None.
            - [Action]: Patches the Content List to the controller.
        Relationship(s):
            - All .loop / .track items associated with controller
        """
        self.content_list = content_list

    def set_home_folder(self, folder_path):
        """
        Description: Sets the home folder path.
        Args:
            - folder_path (str): Path to the home folder.
        Returns:
            - None.
        """
        self.home_folder = folder_path

    def get_home_folder(self):
        """
        Description: Returns the current home folder path.
        Args:
            - None.
        Returns:
            - str: The home folder path.
        """
        return self.home_folder

    # ## ==========================================## #
    # ## ---       CONTROLLER METHODS          --- ## #
    # ## ==========================================## #

    def serialize_loop(self) -> None:
        """
        Description: Takes our valid active_loop and serializes it. Stores it
        as a .loop file in our file manager.
        Args:
            - None
        Returns:
            - None
            - [Action] self.active_loop becomes serialized as a .loop file in
                                    our content list
        Relationship(s):
            - Called by load_loop()
        """
        # Serializes the file to our content list.
        self.file_manager.serialize_loop(self.loop)

    def deserialize_loop(self, file) -> Loop:
        """
        Description: Take a loop file and deserializes it. Reads from a .loop
        file and stores it in temporary memory.
        Args:
            - file (filepath): The file path associated with the loop we're
                                    looking to start in temp memory.
        Returns:
            - loop (Loop): returns loop as loop object.
        Relationship(s):
            - called by load_loop()
        """
        # Deserializes the file to our content list.
        loop = self.file_manager.deserialize_loop(file)

        # Returns Loop object.
        return loop

    def get_load_state(self) -> bool:
        """
        Description: Returns load state.
        Args:
            - None.
        Returns:
            - load_state (bool): If the controller is in load mode.
        Relationship(s):
            - Cannot load objects into buckets or loop area outside of load
                                    mode.
        """
        return self.load_state

    def toggle_load(self):
        """
        Description: Toggles between load mode and non-load mode. Returns
        mode.
        Args:
            - None.
        Returns:
            - Bool: True if now set to load mode, False if load mode is off.
        Relationship(s):
            - If True, next drag will move an object to a position.
        """
        # grab current load_mode
        if self.get_load_state():
            self.load_state = False
        else:
            self.load_state = True

    def process_filename(self):
        """
        Creates string-ified date-time for filename appendage on tracks and
        loops. Uses YMDHMS so all files are always unique and we don't have to
        worry about conflicting file names on creation of new files.
        """
        # Time of file creation
        now = datetime.now()

        # Formats to YYYYMMDDHHSS.
        formatted_now = now.strftime("%Y%m%d%H%M%S")
        return formatted_now

    def create_new_loop(self, name=DEFAULT_LOOP_NAME):
        """
        Create new loop and its project directory. Called when creating a new loop project,
        not when opening an existing project.
        """
        invalid_chars = r'[\\/:*?"|<>\x00 ]'
        clean_name = re.sub(invalid_chars, '_', name)
        project_dir = f"{LOOP_DIR}/{clean_name}"
        # If the project name already exists, add a "_1" until it doesn't exist
        while os.path.isdir(project_dir):
            project_dir += "_1"
        # Make the project path
        os.makedirs(project_dir)
        # Inside the project, make a directory to hold audio files
        audio_dir = project_dir + "/audio"
        os.makedirs(audio_dir)
        # Make the loop and set its name and path
        self.loop = Loop(project_path=project_dir, loop_name=name)

    def export_loop(self):
        """
        Creates a dedicated audio file from the buffer of active_loop's
        play_all() functionality. Stores this audio file as a new track for
        future track editing.
        """
        # Loads current loop's audio files (as if to play) as an array
        # TODO: Load audio files from loop in buffer
        # track_name = f"Track_{self.process_filename()}"
        # audio_file = self.audio_buffer(self.active_loop)

        # Processes audio track from audio file
        # TODO: Process audio files from loop via audio processor
        # new_track = self.audio_processor(track_name, self.no_tracks, \
        # duration, self._no_tracks, audio_file)

        # Serialize new audio track (we don't want to necessarily use it right
        # away)
        # TODO: Install loop serializer
        # self.file_manager.serialize_loop(new_track)

        # TODO: Remove pass once functionality is established.
        pass

    def play_loop(self):
        """
        Plays active loop. Active loop -should- already be loaded into memory
        buffer for instant playback.
        """
        self.loop.play()

    def pause_loop(self):
        """
        Pause active loop. Active loop -should- already be loaded into memory
        buffer for instant playback.
        """
        self.loop.pause()

    def stop_loop(self):
        """Stops active_loop. Active loop -should- already be loaded into
        memory buffer for instant playback.
        """
        self.loop.stop()

    def mute_loop(self):
        """
        Mutes active_loop. Active loop -should- already be loaded into memory
        buffer for instant playback. We don't need mute on buckets.
        """
        # Mutes active_loop
        self.loop.mute()

    def unmute_loop(self):
        """
        Unmutes active_loop. Active loop -should- already by loaded into memory
        buffer for instant playback. We don't need unmute on buckets.
        """
        self.loop.unmute()

    def mute_track(self, pos):
        """
        Mutes selected track position.
        """
        self.loop.mute_track(pos)

    def unmute_track(self, pos):
        """
        Unmutes selected track position.
        """
        self.loop.unmute_track(pos)

    def record_request(self):
        """
        Holds the checks related to recording an audio file into a track
        location in our active_loop.
        """
        # Validate recording request:
        self.validator.is_valid_recording(self.no_tracks,
                                          self.selected_track,
                                          self.active_loop)

        try:
            self._start_recording()
        except Exception as err:
            raise e.RecordingError("Invalid recording location.") from err

    def _start_recording(self):
        """
        Starts recording.
        """
        self.audio_recorder.start_recording(self.no_tracks)

    def _stop_recording(self, position):
        """
        Stops recording. Processes recoding to track.
        """
        # file_path = self.audio_recorder.end_recording()

        # Processes audio track from audio file
        # TODO: Process audio files from loop via audio processor
        # new_track = self.audio_processor(track_name, self.no_tracks, \
        # duration, self._no_tracks, audio_file)

        # Maps audio track to loop position.
        # self.active_loop.import_to_position(new_track, position)

    def move_track(self, from_pos, to_pos):
        """
        Swaps the position of two tracks in the active_loop. User drags the
        track position they are wanting to move into the position they are now
        wanting it to live in -- we store the from / to position and call it
        here.
        """
        active_loop = self.get_active_loop

        # Call loop function move_track
        active_loop.move_track(from_pos, to_pos)

    def clear_track(self, position):
        """
        Description: Removes the track at the specified position from the
        active loop and marks the position as unoccupied.
        Args:
            - position (int): Track position (1-6) to clear.
        Returns:
            - None.
            - [Action]: Removes track from loop and updates occupation status.
        Relationship(s):
            - Called by GUI clear track button functionality.
        """
        pass

    def apply_reverse(self, position):
        """
        Description: Toggles the reverse effect on the track at the specified
        position. If currently reversed, removes reverse; if normal, applies
        reverse.
        Args:
            - position (int): Track position (1-6) to toggle reverse effect.
        Returns:
            - None.
            - [Action]: Toggles track reverse state and refreshes loop buffer.
        Relationship(s):
            - Called by GUI reverse button for individual tracks.
        """
        pass

    def apply_xf1(self, position, value):
        """
        Description: Applies XF1 time dilation effect to the track at the
        specified position. Values greater than 1.0 speed up playback,
        values less than 1.0 slow down playback.
        Args:
            - position (int): Track position (1-6) to apply effect to.
            - value (float): Time dilation factor.
        Returns:
            - None.
            - [Action]: Sets track time dilation and refreshes loop buffer.
        Relationship(s):
            - Called by GUI XF1 control for individual tracks.
        """
        pass

    def apply_xf2(self, position, value):
        """
        Description: Applies XF2 pitch modulation effect to the track at the
        specified position. Positive values raise pitch, negative values
        lower pitch in half-step increments.
        Args:
            - position (int): Track position (1-6) to apply effect to.
            - value (int): Pitch modulation in half-steps.
        Returns:
            - None.
            - [Action]: Sets track pitch modulation and refreshes loop buffer.
        Relationship(s):
            - Called by GUI XF2 control for individual tracks.
        """
        pass

    def solo_track(self, position):
        """
        Description: Sets the track at the specified position for solo
        playback. The track will be played independently of the full loop.
        Args:
            - position (int): Track position (1-6) to solo.
        Returns:
            - None.
            - [Action]: Sets track as the loop to play for solo functionality.
        Relationship(s):
            - Called by GUI solo button for individual tracks.
        """
        pass

    def apply_mix(self, position, balance):
        """
        Description: Applies left/right stereo balance to the track at the
        specified position. Currently a placeholder for future stereo
        processing implementation.
        Args:
            - position (int): Track position (1-6) to apply balance to.
            - balance (float): Balance value (-1.0 to 1.0, left to right).
        Returns:
            - None.
            - [Action]: Placeholder for stereo balance processing.
        Relationship(s):
            - Called by GUI mix/balance controls for individual tracks.
        """
        pass

    @staticmethod
    def create_directories():
        """
        Description: Sets up the necessary directories for the app.
        Args:
            -
        Returns:
            -
        Relationship(s):
            -
        """
        projects_dir = "../projects"  # top level directory
        # add subdirectories to path if not present
        loops_dir = os.path.join(projects_dir, "loops")
        samples_dir = os.path.join(projects_dir, "samples")
        waveform_dir = os.path.join(projects_dir, "waveform_images")

        # exist_ok=True avoids raising err if directories already exist
        os.makedirs(loops_dir, exist_ok=True)
        os.makedirs(samples_dir, exist_ok=True)
        os.makedirs(waveform_dir, exist_ok=True)

    def set_project_home(self, folder_path):
        """
        Description: Sets up the project home directory and creates required
        folder structure.
        Args:
            - folder_path (str): Path to the desired home directory.
        Returns:
            - Path: The project root directory path.
        Relationship(s):
            - Called by GUI when user selects project folder.
        """
        root = self.file_manager.set_home_directory(folder_path)
        self.set_home_folder(str(root))
        return root

    def rename_project_file(self, file_path, new_name):
        """
        Description: Renames a project file or folder.
        Args:
            - file_path (str): Current path of the file to rename.
            - new_name (str): New name for the file.
        Returns:
            - Path: The new file path after renaming.
        Relationship(s):
            - Called by GUI rename functionality.
        """
        return self.file_manager.rename_file(file_path, new_name)

    def delete_project_file(self, file_path):
        """
        Description: Safely deletes a project file by moving it to trash.
        Args:
            - file_path (str): Path of the file to delete.
        Returns:
            - None.
        Relationship(s):
            - Called by GUI delete functionality.
        """
        self.file_manager.delete_file(file_path)

    def record_track(self, position):
        """
        Description: Starts recording to specified track position.
        Stop recording should be handled by separate stop_record_track method.
        Args:
            - position (int): Track position (1-6) to record to.
        Returns:
            - None.
            - [Action]: Starts recording workflow.
        Relationship(s):
            - Called by GUI record button for specific track position.
        """
        self.loop.recording_track = position

    def stop_record_track(self):
        """
        Description: Stops current recording and creates track.
        Args:
            - None.
        Returns:
            - None.
            - [Action]: Stops recording and finalizes track creation.
        Relationship(s):
            - Called by GUI stop recording button.
        """
        self.loop.stop()

    def play_button(self):
        """
        Description: One-click play button. Plays loop_to_play if set,
        otherwise sets active_loop as loop_to_play and plays it.
        Args:
            - None.
        Returns:
            - None.
            - [Action]: Starts playback of appropriate loop.
        Relationship(s):
            - Called by GUI main play button.
        """
        pass

    def pause_button(self):
        """
        Description: One-click pause button. Pauses currently playing loop.
        Args:
            - None.
        Returns:
            - None.
            - [Action]: Pauses current playback.
        Relationship(s):
            - Called by GUI main pause button.
        """
        pass

    def stop_button(self):
        """
        Description: One-click stop button. Stops currently playing loop.
        Args:
            - None.
        Returns:
            - None.
            - [Action]: Stops current playback.
        Relationship(s):
            - Called by GUI main stop button.
        """
        pass

    def save_current_loop(self):
        """
        Description: One-click save button. Serializes active loop with
        auto-generated filename.
        Args:
            - None.
        Returns:
            - None.
            - [Action]: Saves current loop to file.
        Relationship(s):
            - Called by GUI save button.
        """
        filename = f"Loop_{self.process_filename()}.loop"
        self.file_manager.serialize_loop(self.loop, filename)

    def load_loop_from_file(self, file_path):
        """
        Description: One-click load loop button. Complete workflow to load
        loop from file to active loop.
        Args:
            - file_path (str): Path to loop file to load.
        Returns:
            - None.
            - [Action]: Complete loop loading workflow.
        Relationship(s):
            - Called by GUI load loop functionality.
        """
        # Save current loop if there is one
        if self.loop:
            self.save_current_loop()

        # Load new loop
        new_loop = self.deserialize_loop(file_path)
        self.loop = new_loop

    def new_loop_button(self):
        """
        Description: One-click new loop button. Saves current loop and
        creates new blank loop.
        Args:
            - None.
        Returns:
            - None.
            - [Action]: Complete new loop creation workflow.
        Relationship(s):
            - Called by GUI new loop button.
        """

        # Create new blank loop
        loop_name = f"Loop_{self.process_filename()}"
        new_loop = Loop(loop_name=loop_name)
        self.loop(new_loop)

        # TODO: Clear GUI
        # self.gui.clear_loop_area()

    def export_loop_as_track(self):
        """
        Description: One-click export loop button. Converts current loop
        to single track file.
        Args:
            - None.
        Returns:
            - None.
            - [Action]: Exports loop as track file.
        Relationship(s):
            - Called by GUI export button.
        """
        # TODO: Mix loop to single audio file
        # mixed_audio = self.audio_buffer.mix_loop(self.active_loop)

        # TODO: Create track from mixed audio
        # track_name = f"Track_{self.process_filename()}"
        # new_track = self.audio_processor.create_track_from_audio(
        #     track_name, mixed_audio, self.no_tracks)

        # TODO: Serialize track
        # self.file_manager.serialize_track(new_track)
        pass
