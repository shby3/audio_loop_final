"""This file sketches out high-level pseudocode of main program
functionalities.

Initial Author: Daniel Kaufman
"""

"""
open_project()
    this function is called as soon as GUI launches
    user input selects a project (abstracted as a pickle file)
        otherwise "new project" is selected"


    ***When New Project is selected***
    record_new_track()
        new directory is created if one does not already exist, "new_tracks"
        call recording_type()
            described below
        new .wav file is created in record_track.py; output --> filepath
        create new TrackList class to track this new project
        create new TrackNode(filepath) to hold metadata about track and
        filepath
        save Tracklist as pickle file to save ongoing progress
            (unsure if timing of this "save progress" is correct at this point
            in the program)

    play_all_tracks()
        description is found later in file
        (default state is without pitch modulation, time, dilation, or
        reversed since the track is new)


    ***When A Previous Project is selected***
    unpack_project():
        data structure is unpickled
    file verification ():
        verification of .wav files in structure are in target directory
            errors raised if files are not found in target directory
                resolution steps needed?
    track_filters_applied()
        .wav files are converted to NumPy arrays based on filters selected in 
        data structure  (pitch modulation, time, dilation, or reversed)
    load_tracks()
        tracks are loaded into GUI


play_all_tracks()
    scheduler_program()
        time delays applied as needed to sequence all tracks starting at the 
        same time
        schedule established for each track based TrackNode._length
    TrackNode._file loaded based on filter settings
    each TrackNode is played as a seperate thread, and is queued by the 
    scheduler

pitch_modulation(track_number)
    iterates through TrackList until target track is reached
    .wav file is converted as NumPy array
    NumPy array is dilated as saved in TrackNode._file

time_dilation(track_number)
    iterates through TrackList until target track is reached
    .wav file is converted as NumPy array
    NumPy array is modulated as saved in TrackNode._file

reverse(track_number)
    iterates through TrackList until target track is reached
    .wav file is converted as NumPy array
    NumPy array is reversed as saved in TrackNode._file     

recording_type()
    prompts a user if the new track to be recorded is in mono or stereo
    output --> defines if channel should be streamed to track at 1 or 2 
    channels
"""
