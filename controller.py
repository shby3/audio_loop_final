from datetime import datetime
from loop import Loop
import exceptions as e
import os


class Controller:
    """
    Description: Represents the orchestrator between all aspects in our app.
    The Controller in this case owns the gui, the audio recorder, the processor
    the buffer, and the player. It also points to the currently active Loop and
    Buckets page.

    Args:
    [NOTE: All Arguments will have dedicated getter / setter methods with
    atypical setter_methods called below in 'Methods' area]
        - no_tracks (int): a global toggle to determine if we're recording in
                                    mono or stereo.
        - track_positions (map(int, bool)): A map of all six allotted slots
                                    available to a loop. True implies currently
                                    selected slot is full, False implies not.
        - active_loop (obj: Loop): The loop we're actively adjusting.
        - loop_to_play (obj: Loop): Generally, the same as active_loop, but
                                    occasionally, a bucket loop or a track (in
                                    solo)
        - selected_track (obj: Track): The track we're currently manipulating.
                                    The selected track has a GUI response
                                    indicator (a 'light') so we visually see
                                    what we're touching.
        - load_state (bool): Toggles system to "loading" mode. Defaults to
                                    False, on toggle, to True. This is a safety
                                    check that prevents undesired loading on
                                    mouse drag.
        - move_state (bool): Toggles system to "moving" mode. Defaults to False
                                    on toggle, to True. This is a safety check
                                    that prevents undesired moving on mouse
                                    drag.

    Components:
    [NOTE] All components have getter / setter methods.
        - File Manager: Responsible for serialization / deserialization of loop
                                    and track items.
        - Content List: The file structure associated with storing items in-
                                    memory.
        - GUI: the graphic user interface of the controller, manages input
                                    devices
        - Validator: the validation service the controller uses to determine
                                    if GUI directives are valid before
                                    execution.
        - Audio Recorder: The device used for recording, manages audio input
                                    device.
        - Audio Processor: The device used for mapping a recording object to
                                    a dedicated track structure.
        - Audio Buffer: The device used to take a Loop's related audio files
                                    and output to stereo numpy array.
        - Audio Player: The device used to actually play the loaded audio file
                                    on a user's audio output device.
        - Buckets Module: The device used for immediate playback purposes,
                                    stores numpy arrays of loops in a playable
                                    state for instant / immediate playback.

    Methods:
        - toggle_tracks(): Takes a track configured for mono and sets it to
                                    stereo or visa-versa.
        - get_no_tracks(): Returns the channel config currently set in
                                    controller.
        - get_is_track_occupied(position): Takes a loop track position, and
                                    returns if the associated position is open
                                    (True) or full (False).
        - set_track_position_occupied(position, bool): Takes a loop track
                                    position, and sets it to occupied or
                                    unoccupied. If called with False, sets to
                                    unoccupied, if set with True, sets to
                                    occupied.
        - update_all_tracks_occupied_status(): Takes a loop object, iterates
                                    over all tracks in the loop and ensures
                                    track_occupied statuses are updated
                                    appropriately.
        - get_selected_track(): Returns the last selected loop track position.
        - select_record_track_position (position: int): Promotes GUI response
                                    when track-specific functionality is
                                    selected (i.e. if solo is select on track 3
                                    - indicator for track 3 is turned 'on' and
                                    self.selected_track is updated.)
        - get_loop_to_play(): Returns a loop object selected for playback not
                                    in the loop design area.
        - set_loop_to_play(): Sets the loop from a bucket (or a solo track),
                                    for immediate playback on solo or loop
                                    bucket play buttons.
        - get_active_loop(): Returns the active loop object.
        - set_active_loop(loop: Loop): sets the loop named as Loop, to
                                    self.active_loop. Process by which we
                                    re-serialize the active loop, clear the
                                    loop design area, and load a separate loop
                                    to that area.
        - serialize_loop (obj: Loop): Takes active loop object mapping and
                                    saves it to .loop file.
        - deserialize_loop (obj: Loop): Takes a .loop file and reads it, stores
                                    it in temp memory for future use.
        - get_load_state(): Returns a boolean if controller is currently
                                    toggled to "loading".
        - toggle_load(): Sets a boolean to put the controller in "load" mode.
                                    The next mouse drag will be from an object:
                                    Loop or Track to a position.
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
        - play_bucket_loop: Plays the loop currently pointed to by
                                    loop_to_play in loop bucket area. Initiates
                                    a clock to return time since play was
                                    clicked for future pause.
        - pause_loop : Pauses the loop currently in the loop design area.
        - pause_bucket_loop : Pauses the audio content being called upon
                                    outside of the loop design area.
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
        - load_to_bucket (loop, bucket_number): Load loop to bucket
        - play_bucket (bucket_number): Play loop from bucket
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
        self.active_loop = None

        # Map of the slots of the loop, controlled by GUI, checked here first
        self.track_occupied = {
                1: False,
                2: False,
                3: False,
                4: False,
                5: False,
                6: False
            }

        # The loop we're actively playing
        self.loop_to_play = None

        # The current track position we're manipulating.
        self.selected_track = None

        # Components:
        self.validator = None
        self.gui = None
        self.audio_recorder = None
        self.audio_processor = None
        self.audio_buffer = None
        self.audio_player = None
        self.file_manager = None
        self.content_list = None

        # Specific mode toggles - changes to specific modes:
        self.load_state = False     # Next drag is obj -> pos
        self.move_state = False     # Next drag is internal pos -> pos.

        # Sets home directory (default to current file's directory)
        self.home_folder = os.path.dirname(__file__)

    # ## ==========================================## #
    # ## --- COMPONENT GETTER / SETTER METHODS --- ## #
    # ## ==========================================## #

    def get_audio_recorder(self) -> object:
        """
        Description: Returns current audio recorder settings.
        Args:
            - None.
        Returns:
            - Recorder (obj): The recorder object.
        Relationship(s):
            - Used for recording.
        """
        return self.audio_recorder

    def set_audio_recorder(self, audio_recorder):
        """
        Description: Attaches a new audio_recorder with settings.
        Args:
            - audio_recorder (obj): An audio record class object.
        Returns:
            - None.
            - [Action]: Patches the audio recorder to the controller.
        Relationship(s):
            - Used for recording.
        """
        self.audio_recorder = audio_recorder

    def get_audio_processor(self):
        """
        Description: Returns current audio processor settings.
        Args:
            - None.
        Returns:
            - Processor (obj): The Processor object.
        Relationship(s):
            - Used for audio processing.
        """
        return self.audio_processor

    def set_audio_processor(self, audio_processor):
        """
        Description: Attaches a new audio_processor with settings.
        Args:
            - audio_processor (obj): An audio processor class object.
        Returns:
            - None.
            - [Action]: Patches the audio processor to the controller.
        Relationship(s):
            - Used for audio processing.
        """
        self.audio_processor = audio_processor

    def get_audio_buffer(self):
        """
        Description: Returns current audio buffer settings.
        Args:
            - None.
        Returns:
            - Loader (obj): The Loader object.
        Relationship(s):
            - Used for audio loading before playback.
        """
        return self.audio_buffer

    def set_audio_buffer(self, audio_buffer):
        """
        Description: Attaches a new audio_buffer with settings.
        Args:
            - audio_loading (obj): An audio buffer class object.
        Returns:
            - None.
            - [Action]: Patches the audio buffer to the controller.
        Relationship(s):
            - Used for audio loading before playback.
        """
        self.audio_buffer = audio_buffer

    def get_audio_player(self):
        """
        Description: Returns current audio player with settings.
        Args:
            - None.
        Returns:
            - Player (obj): The Audio Player object.
        Relationship(s):
            - Used for audio playback.
        """
        return self.audio_player

    def set_audio_player(self, audio_player):
        """
        Description: Attaches a new audio_player with settings.
        Args:
            - audio_player (obj): An audio player class object.
        Returns:
            - None.
            - [Action]: Patches the audio player to the controller.
        Relationship(s):
            - Used for audio playback.
        """
        self.audio_player = audio_player

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

    def toggle_tracks(self) -> None:
        """
        Description: Sets the channel config for recording. Toggles between
        mono or stereo.
        Args:
            - None.
        Returns:
            - None.
            - [Action] Toggles known 'no_tracks' from 1 to 2 or 2 to 1.
        Relationship(s):
            - Necessary for recording. Stored in Track via loop.
        """
        if self.no_tracks == 1:
            self.no_tracks = 2
        else:
            self.no_tracks = 1

    def get_no_tracks(self) -> int:
        """
        Description: Gets the channel config for recording.
        Args:
            - None.
        Returns:
            - Channel config associated with next recording. self.no_tracks
        Relationship(s):
            - Necessary for recording. Stored in Track via loop.
        """
        return self.no_tracks

    def get_is_track_occupied(self, position: int) -> bool:
        """
        Description: Returns whether entered position is full or not. True
        means slot is occupied, False means unoccupied.
        Args:
            - position (int): a track position map location.
        Returns:
            - Bool: True if is filled, False if empty.
        Relationship(s):
            - Called as a validator on other functions.
        """
        return self.track_occupied[position]

    def set_track_position_occupied(self, position, is_occupied) -> None:
        """
        Description: Sets a track position to Occupied (if currently
        unoccupied), or vice-versa. If is_occupied matches current position,
        leave it as-is.
        Args:
            - position (int): a track position map location
            - is_occupied (bool): what to set the location to
        Returns:
            - None.
            - [Action] sets self.active_loop position to the bool is_occupied.

        Relationship(s):
            - Should be touched by all track related methods in our loop.
        """
        if self.track_occupied[position] != is_occupied:
            self.track_occupied[position] = is_occupied

    def update_all_tracks_occupied_status(self) -> None:
        """
        Description: Sets all track positions as either occupied or unoccupied
        as dictated by loop. If is_occupied matches current position,
        leave it as-is.
        Args:
            - None.
        Returns:
            - None.
            - [Action] sets self.track_occupied position to True if related
                                        tracks in loop are occupied.
        Relationship(s):
            - Should be touched by all track related methods in our loop.
        """
        # Reset items
        self.track_occupied = {i: False for i in range(1, 7)}

        # For active loop, if loop doesn't exist, we're done.
        loop = self.get_active_loop()

        # if the active loop has a track in a position, set its occupied to
        # True, otherwise to False.

        for track_no, track in loop.loop_tracks.items():
            if track is not None:
                self.track_occupied[track_no] = True

    def get_record_track_position(self) -> int:
        """
        Description: Returns the last selected track position.
        Args:
            - None.
        Returns:
            - Int: The loop track position related to the last position clicked
            in the GUI.
        Relationship(s):
            - TBD.
        """
        return self.selected_track

    def select_record_track_position(self, position) -> None:
        """
        Description: Selects track position for recording.
        Args:
            - position (int): a track position map location.
        Returns:
            - None:
            - [Action]: GUI response turns selected track "on" and sets self.
            selected_track to it!
        Relationship(s):
            - TBD.
        """
        # TODO: Un-comment when GUI is connected.
        # self.gui.toggle_position(position)
        self.selected_track = position

    def get_loop_to_play(self) -> Loop:
        """
        Description: Gets the associated loop or solo track object attempting
        to be played outside of loop design area.
        Args:
            - None.
        Returns:
            - Loop object.
        Relationship(s):
            - TBD:
        """
        return self.loop_to_play

    def set_loop_to_play(self, loop: Loop) -> None:
        """
        Description: On click of either a loop bucket or a solo track, sets
        playable content to self.loop_to_play.
        Args:
            - loop (Loop): The object we're attempting to play.
        Returns:
            - None.
            - [Action]: sets to self.loop_to_play
        Relationship(s):
            - TBD:
        """
        self.loop_to_play = loop

    def get_active_loop(self) -> Loop:
        """
        Description: Gets the associated loop we're manipulating in the loop
        design area.
        Args:
            - None.
        Returns:
            - self.active_loop (Loop): The loop we're currently manipulating.
        Relationship(s):
            - Called by all actions on the loop to ensure we're only touching
            our active
            loop.
        """
        return self.active_loop

    def set_active_loop(self, loop: Loop) -> None:
        """
        Description: On load_loop() method, sets active_loop to loop object.
        Assumes desired loop object has been appropriately deserialized and
        previously current loop has been serialized.
        Args:
            - loop (Loop): our new active_loop
        Returns:
            - None
            - [Action] sets self.active_loop to loop
        Relationship(s):
            - Called by load_loop()
        """
        self.active_loop = loop

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
        # Gets our active_loop
        loop = self.get_active_loop()

        # Serializes the file to our content list.
        self.file_manager.serialize_loop(loop)

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

    def load_object(self, obj_file_name, location) -> None:
        """
        Description: Takes a loop object not currently stored as active_loop,
        deserializes it so it can map to the GUI, ensures all audio track files
        in their current state are ready for play back, the sets active_loop to
        loop object.
        Args:
            - obj_file_name(string): The file name associated with the object.
            - position(string): The name of the associated position to move to.
        Returns:
            - None
            [Action] (Optional): If loop is being moved to loop area,
            self.active_loop will change to new loop.
        Relationship(s):
            - When load button is clicked, should call something akin to
            "register drag" which will return an object and a location. Should
            also map to self.selected_track (if location is a track).
        TODO: Simplify this. Validation probably shouldn't be here directly. It
        should be sent as one piece to validation.py and finished from there
        with helpers.
        """
        # Confirm load_mode. If not in load mode, reject request.
        if not self.get_load_state():
            raise e.InvalidState("Cannot load without 'LOAD' selection.")

        # Get object type.
        file_type = self.validator.get_extension(obj_file_name)

        # Confirm that desired file path is a valid loop type.
        if not self.validator.is_valid_loop(obj_file_name):
            raise e.InvalidLoop(f"The loop called {obj_file_name} is not a\
                valid loop.")

        # If object is a Loop, validate position is either loop area or bucket.
        if file_type == "loop":

            # Reads loop_file_name as loop --> maps object as loop in memory
            # TODO: Install loop deserializer.
            active_loop = self.file_manager.deserialize_loop(obj_file_name)

            if self.validator.is_loop_area(location):
                # Serializes active_loop and stores it as a .loop file
                # TODO: Install loop serializer.
                self.file_manager.serialize_loop(self.active_loop)

                # Maps loop object to GUI
                # TODO: Install UI label mapper
                self.gui.map_labels(active_loop)

                # Loads audio tracks from loop to buffer
                # TODO: Load audio files from loop in buffer
                self.audio_player.load_from_loop(active_loop)

                self.set_active_loop(active_loop)

            if self.validator.is_bucket(location):

                # Map the loop to the bucket. We don't serialize because we
                # can't edit from buckets.
                self.buckets_module.load_bucket(active_loop)

        else:
            # Deserialize track name from file.
            active_track = self.file_manager.deserialize_track(obj_file_name)

            # If mono and position is still open, set the deserialized track
            # object to the position.
            position = self.get_selected_track()

            if not self.get_is_track_occupied(position) and \
                    active_track.get_channel_config() == 1:
                self.active_loop.set_loop_track(location, active_track)

            # If stereo, and both the asked for (and asked for plus 1)
            # positions are open, add both serialized tracks to position and
            # position + 1.
            if not self.get_is_track_occupied(position) and not \
                self.get_is_track_occupied(position + 1) and \
                    active_track.get_channel_config() == 2:

                second_track = self.file_manager.deserialize_track(
                    self.active_loop
                    .loop_tracks[position]
                    .related_path)

                self.active_loop.set_loop_track(position + 1, second_track)

    def update_loop(self):
        """
        After a change has been made to a track in a loop, this method re-loads
        the loop object so it is ready for immediate playback.
        TODO: Remove pass after buffer is complete.
        """
        # Re-loads audio tracks from loop to buffer
        # TODO: Load audio files from loop in buffer
        # self.audio_buffer(self.active_loop)
        pass

    def create_new_loop(self):
        """
        Serializes active loop and clears all related data from GUI and buffer.
        Creates new loop object, with empty mappings ready for editing.
        """
        # Confirm that active_loop is actually pointing to something
        if not self.validator.is_valid_loop(self.active_loop):
            raise e.InvalidLoop("Cannot store active loop.")

        # Serializes current loop
        # TODO: Install loop serializer
        # self.file_manager.serialize_loop(self.active_loop)

        # Creates new loop object - this loop object is currently deserialized
        # (in memory).
        # TODO: Ensure this process actually makes sense with loop creation is
        # complete.
        loop_name = self.process_filename()
        new_loop = Loop()
        new_loop.set_name(loop_name)

        # Maps loop object to GUI
        # TODO: Install UI label mapper
        # self.gui.map_labels(active_loop)

        # Sets new loop to active_loop
        self.active_loop = new_loop

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
        target_loop = self.get_active_loop()

        # Confirm that target_loop is actually pointing to something
        if not self.validator.is_valid_loop(target_loop):
            raise e.InvalidLoop("Missing active loop.")

        # Plays.
        self.audio_player.play(target_loop)

    def play_bucket_loop(self):
        """
        Plays a bucket loop. Bucket loop will not already be in memory; as such
        we need to mix the loop before playback.
        """
        target_loop = self.get_loop_to_play()

        # Confirm that target_loop is actually pointing to something
        if not self.validator.is_valid_loop(target_loop):
            raise e.InvalidLoop("Missing playback loop.")

        # Sends content to buffer. Only loop in loop area is mixed already.
        self.active_buffer.mix_loop(target_loop)

        # Plays.
        self.audio_player.play(target_loop)

    def pause_loop(self):
        """
        Pause active loop. Active loop -should- already be loaded into memory
        buffer for instant playback.
        """
        # Target loop is either a bucket, or our active loop.
        target_loop = self.get_active_loop()

        # Confirm that target_loop is actually pointing to something
        if not self.validator.is_valid_loop(target_loop):
            raise e.InvalidLoop("Missing active loop.")

        self.audio_player.pause(target_loop)

    def pause_bucket_loop(self):
        """
        Pause bucket loop. Bucket loop should be in memory if this button is
        selected (it would need to be buffered to play.)
        """
        # Target loop is either a bucket, or our active loop.
        target_loop = self.get_loop_to_play()

        # Confirm that target_loop is actually pointing to something
        if not self.validator.is_valid_loop(target_loop):
            raise e.InvalidLoop("Missing active loop.")

        self.audio_player.pause(target_loop)

    def stop_loop(self):
        """Stops active_loop. Active loop -should- already be loaded into
        memory buffer for instant playback.
        """
        # Target loop is either a bucket, or our active loop.
        target_loop = self.get_active_loop()

        # Confirm that target_loop is actually pointing to something
        if not self.validator.is_valid_loop(target_loop):
            raise e.InvalidLoop("Missing active loop.")

        self.audio_player.stop(target_loop)

    def stop_bucket_loop(self):
        """
        Description: Stops bucket loop.
        TODO: We -=may=- need to re-buffer the active_loop when complete.
        """
        # Target loop is either a bucket, or our active loop.
        target_loop = self.get_loop_to_play()

        # Confirm that target_loop is actually pointing to something
        if not self.validator.is_valid_loop(target_loop):
            raise e.InvalidLoop("Missing active loop.")

        self.audio_player.stop(target_loop)

    def mute_loop(self):
        """
        Mutes active_loop. Active loop -should- already be loaded into memory
        buffer for instant playback. We don't need mute on buckets.
        """
        # Mutes active_loop
        self.audio_player.mute(self.active_loop)

    def unmute_loop(self):
        """
        Unmutes active_loop. Active loop -should- already by loaded into memory
        buffer for instant playback. We don't need unmute on buckets.
        """
        self.audio_player.unmute(self.active_loop)

    def mute_track(self, pos):
        """
        Mutes selected track position.
        """
        active_loop = self.get_active_loop()

        # Validates track position
        if self.get_is_track_occupied(pos):
            active_loop.mute_track(pos)

        # Updates loop
        self.update_loop(active_loop)

    def unmute_track(self, pos):
        """
        Unmutes selected track position.
        """
        active_loop = self.get_active_loop()

        # Validates track position
        if self.get_is_track_occupied(pos):
            active_loop.unmute_track(pos)

        # Updates loop
        self.update_loop(active_loop)

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

    def adjust_track_volume(self, position, volume):
        """
        Description: Adjusts the volume level for a track at the specified
        position in the active loop.
        Args:
            - position (int): Track position (1-6) to adjust volume for.
            - volume (float): Volume level between 0.0 and 1.0.
        Returns:
            - None.
            - [Action]: Updates track volume and refreshes loop buffer.
        Relationship(s):
            - Called by GUI volume controls for individual tracks.
        """
        if self.get_is_track_occupied(position):
            track = self.active_loop.loop_tracks[position]
            track.set_volume(volume)
            self.update_loop()

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
        if self.get_is_track_occupied(position):
            self.active_loop.remove_track(position)
            self.set_track_position_occupied(position, False)
            self.update_loop()

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
        if self.get_is_track_occupied(position):
            track = self.active_loop.loop_tracks[position]
            track.set_reverse(not track.is_reversed)
            self.update_loop()

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
        if self.get_is_track_occupied(position):
            track = self.active_loop.loop_tracks[position]
            track.set_time_dilation(value)
            self.update_loop()

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
        if self.get_is_track_occupied(position):
            track = self.active_loop.loop_tracks[position]
            track.set_pitch_modulation(value)
            self.update_loop()

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
        if self.get_is_track_occupied(position):
            track = self.active_loop.loop_tracks[position]
            self.set_loop_to_play(track)

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
        if self.get_is_track_occupied(position):
            # TODO: Implement stereo balance processing
            pass

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
        # Set selected track position
        self.select_record_track_position(position)

        # Validate and start recording
        self.record_request()

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
        self._stop_recording(self.selected_track)

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
        # If no loop_to_play is set, use active_loop
        if self.loop_to_play is None:
            self.set_loop_to_play(self.active_loop)

        # Play the selected loop
        if self.loop_to_play:
            self.audio_player.play(self.loop_to_play)

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
        if self.loop_to_play:
            self.audio_player.pause(self.loop_to_play)

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
        if self.loop_to_play:
            self.audio_player.stop(self.loop_to_play)

    def load_to_bucket(self, loop: Loop, bucket_number: int):
        """
        Description: One-click load loop to bucket functionality.
        Args:
            - loop (Loop): Loop object to load to bucket.
            - bucket_number (int): Bucket number (1-10) to load to.
        Returns:
            - None.
            - [Action]: Loads loop to specified bucket.
        Relationship(s):
            - Called by GUI bucket load functionality.
        """
        # TODO: Implement bucket module integration
        # self.buckets_module.load_bucket(loop, bucket_number)
        pass

    def play_bucket(self, bucket_number):
        """
        Description: One-click play bucket functionality.
        Args:
            - bucket_number (int): Bucket number (1-6) to play.
        Returns:
            - None.
            - [Action]: Sets bucket loop as loop_to_play and starts playback.
        Relationship(s):
            - Called by GUI bucket play buttons.
        """
        # TODO: Get loop from bucket and set as loop_to_play
        # bucket_loop = self.bucket.get_bucket_loop(bucket_number)
        # self.set_loop_to_play(bucket_loop)
        # self.play_button()
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
        if self.active_loop:
            filename = f"Loop_{self.process_filename()}.loop"
            self.file_manager.serialize_loop(self.active_loop, filename)

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
        # Save current loop if it exists
        if self.active_loop:
            self.save_current_loop()

        # Load new loop
        new_loop = self.deserialize_loop(file_path)
        self.set_active_loop(new_loop)

        # Update track occupation status
        self.update_all_tracks_occupied_status()

        # TODO: Update GUI with new loop data
        # self.gui.map_labels(new_loop)

        # TODO: Load audio to buffer
        # self.audio_buffer.load_from_loop(new_loop)

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
        # Save current loop if it exists
        if self.active_loop:
            self.save_current_loop()

        # Create new blank loop
        loop_name = f"Loop_{self.process_filename()}"
        new_loop = Loop(loop_name)
        self.set_active_loop(new_loop)

        # Reset track occupation status
        self.track_occupied = {i: False for i in range(1, 7)}

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
        if self.active_loop:
            # TODO: Mix loop to single audio file
            # mixed_audio = self.audio_buffer.mix_loop(self.active_loop)

            # TODO: Create track from mixed audio
            # track_name = f"Track_{self.process_filename()}"
            # new_track = self.audio_processor.create_track_from_audio(
            #     track_name, mixed_audio, self.no_tracks)

            # TODO: Serialize track
            # self.file_manager.serialize_track(new_track)
            pass
