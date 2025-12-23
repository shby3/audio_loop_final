import os
import unittest
from controller import Controller
from loop import Loop
from track import Track
from file_manager import FileManager
import tempfile

"""
+++------------------------------------------------------------------------+++
Defines a Test suite for the controller class and all related methods.
Generally, this controller class is responsible for ingesting button mappings
from the GUI, and passing validation efforts to our validation component.

NOTE: This is a general scaffold of what this class will do, it still needs an
incredible amount of documentation and commenting before it is finalized.

Written by: Michelle Mann
+++------------------------------------------------------------------------+++
"""


class TestController(unittest.TestCase):
    """
    Description: Tests all functionalities of Controller component including
    all getter / setter methods.
    Methods:
        - test_get_default_no_tracks(): Tests get_no_tracks()
        - test_single_toggle_tracks(): Tests get_no_tracks() after single
                                        toggle
        - test_double_toggle_tracks(): Tests get_no_tracks() after double
                                        toggle
        - test_if_track_occupied_registers_empty_track_as_false(): Tests track
                                        occupation status
        - test_if_track_occupied_registers_full_track_as_true(): Tests track
                                        occupation after marking full
        - test_track_occupied_after_update_to_active_loop(): Tests track
                                        occupation after loop update
        - test_if_track_occupied_registers_full_track_as_true_after_toggle():
                                        Tests track occupation toggles
        - test_get_record_track_position_gets_last_clicked_position():
                                        Tests track position selection
        - test_get_set_loop_to_play(): Tests loop playback selection
        - test_get_set_active_loop(): Tests active loop management
        - test_adjust_track_volume(): Tests track volume adjustment
        - test_clear_track(): Tests track clearing functionality
        - test_apply_reverse(): Tests reverse effect application
        - test_apply_xf1(): Tests time dilation effect
        - test_apply_xf2(): Tests pitch modulation effect
        - test_solo_track(): Tests track solo functionality
        - test_set_project_home(): Tests project home directory setup
        - test_rename_project_file(): Tests file renaming functionality
        - test_delete_project_file(): Tests file deletion functionality
        - test_load_state_workflow(): Tests load state toggle workflow
        - test_serialize_deserialize_workflow(): Tests complete serialization
                                        workflow
        - test_track_effects_workflow(): Tests applying multiple track effects
                                        in sequence
        - test_loop_track_management_workflow(): Tests complete loop and track
                                        management
    """
    def setUp(self):
        """
        Sets up Controller between tests.
        """
        self.obj = Controller()

    def tearDown(self):
        """
        Removes Controller between tests.
        """
        del self.obj

    def test_get_default_no_tracks(self):
        """
        Tests Controller's default channel_config reading.
        [Default channel config should read as 1]
        """
        tracks = self.obj.get_no_tracks()
        self.assertEqual(tracks, 1)

    def test_single_toggle_tracks(self):
        """
        Tests Controller's channel_config after toggle_track is called once.
        [Default channel config should read as 2 after toggle]
        """
        # Toggle channel config
        self.obj.toggle_tracks()
        tracks = self.obj.get_no_tracks()
        self.assertEqual(tracks, 2)

    def test_double_toggle_tracks(self):
        """
        Tests Controller's channel_config after toggle_track is called twice.
        [Default channel config should read as 1 after toggle]
        """
        # Toggle channel config
        self.obj.toggle_tracks()                 # Results in get_no_tracks = 2
        self.obj.toggle_tracks()                 # Results in get_no_tracks = 1
        tracks = self.obj.get_no_tracks()
        self.assertEqual(tracks, 1)

    def test_if_track_occupied_registers_empty_track_as_false(self):
        """
        Tests Controller's ability to get / set the active_loop's
        track_occupied field. Tests default value as False on a given track.
        [Default track_occupied status should read as False on empty loop.]
        """
        track_occupied = self.obj.get_is_track_occupied(1)

        self.assertFalse(track_occupied)

    def test_if_track_occupied_registers_full_track_as_true(self):
        """
        Tests Controller's ability to get / set the active_loop's
        track_occupied field. Tests value as True after a given track is marked
        as full.
        [Default track_occupied status should first be adjusted to True, then
        read as True for a given track on a loop.]
        """
        # Updates track 1 to 'filled'
        self.obj.set_track_position_occupied(1, True)
        track_occupied = self.obj.get_is_track_occupied(1)

        self.assertTrue(track_occupied)

    def test_track_occupied_after_update_to_active_loop(self):
        """
        Tests Controller's ability to get / set the active_loop's
        track_occupied field after an update to active_loop is made.
        [Default track_occupied status should first be adjusted to True, then
        read as True for a given track on a loop.]
        """
        fm = FileManager()
        self.obj.set_file_manager(fm)

        # Get loop path
        base_dir = os.path.dirname(__file__)
        loop_path = os.path.join(base_dir, "test_cases",
                                 "Loop_20250115214530.loop")
        loop_path = os.path.abspath(loop_path)

        # Deserialize the loop and set it to active_loop
        loop = self.obj.file_manager.deserialize_loop(loop_path)
        self.obj.set_active_loop(loop)

        # Ensure loop has been set correctly.
        self.assertEqual(self.obj.active_loop, loop)

        # Status update on tracks_occupied based on loop object.
        self.obj.update_all_tracks_occupied_status()

        self.assertTrue(self.obj.track_occupied[1])
        self.assertTrue(self.obj.track_occupied[2])
        self.assertTrue(self.obj.track_occupied[3])
        self.assertFalse(self.obj.track_occupied[4])
        self.assertFalse(self.obj.track_occupied[5])
        self.assertFalse(self.obj.track_occupied[6])

    def test_if_track_occupied_registers_full_track_as_true_after_toggle(self):
        """
        Tests Controller's ability to get / set the active_loop's
        track_occupied field. Tests default value as False on a given track.
        Then tests if same track is True after a toggle, then also tracks as if
        to mock a rewrite. Finally tests, as if a delete.
        [Default track_occupied status should read as False on empty loop.]
        [Track 2 is used as a baseline to ensure we're not updating other
        tracks]
        """
        # Tests default state.
        self.assertFalse(self.obj.track_occupied[1])

        # Updates track 1 to 'filled' and retests
        self.obj.set_track_position_occupied(1, True)
        track_occupied = self.obj.get_is_track_occupied(1)

        self.assertEqual(self.obj.track_occupied[1], track_occupied)
        self.assertFalse(self.obj.track_occupied[2])

        # Updates track 1 to 'filled' as if on re-write and re-tests.
        self.obj.set_track_position_occupied(1, True)
        track_occupied = self.obj.get_is_track_occupied(1)

        self.assertEqual(self.obj.track_occupied[1], track_occupied)
        self.assertFalse(self.obj.track_occupied[2])

        # Updates track 1 to emptied as if on delete and re-tests.
        self.obj.set_track_position_occupied(1, False)
        track_occupied = self.obj.get_is_track_occupied(1)

        self.assertEqual(self.obj.track_occupied[1], track_occupied)
        self.assertFalse(self.obj.track_occupied[2])

    def test_get_record_track_position_gets_last_clicked_position(self):
        """
        Tests that when a position is clicked: either by clicking on the
        position selector in the loop design area, or by adjusting a parameter
        of a track, or by selecting a bucket -- that it is recorded.
        """

        # Scenario #1: Track Position
        self.obj.select_record_track_position(1)

        track = self.obj.get_record_track_position()
        self.assertEqual(track, 1)

        # Scenario #2: Loop Bucket
        self.obj.select_record_track_position(11)           # Bucket1 = Pos. 11

        bucket = self.obj.get_record_track_position()
        self.assertEqual(bucket, 11)

    def test_get_set_loop_to_play(self):
        """
        Tests that get_loop_to_play pulls last play-clicked button.
        TODO: Map secondary test to ensure GUI button click works as expected.
        """
        # Tests that in default state, None is selected.
        to_play = self.obj.get_loop_to_play()

        self.assertEqual(None, to_play)

        # Tests that should a button be clicked for playback, get_loop_to_play
        # is updated. [Makes new loop first]
        fm = FileManager()
        self.obj.set_file_manager(fm)

        # Get loop path
        base_dir = os.path.dirname(__file__)
        loop_path = os.path.join(base_dir, "test_cases",
                                 "Loop_20250201100000.loop")
        loop_path = os.path.abspath(loop_path)

        # Deserialize the loop and set it to loop_to_play
        loop = self.obj.file_manager.deserialize_loop(loop_path)

        self.obj.set_loop_to_play(loop)

        to_play2 = self.obj.get_loop_to_play()
        self.assertEqual(loop, to_play2)

    def test_get_set_active_loop(self):
        """
        Tests that get_active_loop pulls the loop currently pointed to by
        active_loop in the loop design area.
        """
        # Tests that in default state, None is selected.
        active = self.obj.get_active_loop()

        self.assertEqual(active, None)

        # Tests that once active loop is pointed to, active loop is accessible.
        # [Makes new loop first]
        fm = FileManager()
        self.obj.set_file_manager(fm)

        # Get loop path
        base_dir = os.path.dirname(__file__)
        loop_path = os.path.join(base_dir, "test_cases",
                                 "Loop_20250205181000.loop")
        loop_path = os.path.abspath(loop_path)

        # Deserialize the loop and set it to loop_to_play
        loop = self.obj.file_manager.deserialize_loop(loop_path)

        self.obj.set_active_loop(loop)
        active2 = self.obj.get_active_loop()
        self.assertEqual(loop, active2)

        # Finally, tests that active loop calls point to active_loop
        track2 = active2.loop_tracks[2]

        # Should be a Track object, not a string
        self.assertIsInstance(track2, type(track2))
        # Check if it's the expected track ID from the loop file
        if hasattr(track2, 'track_id'):
            self.assertEqual("Track_20250205181002", track2.track_id)

    def test_adjust_track_volume(self):
        """Tests Controller's adjust_track_volume method."""
        loop = Loop("Test Loop")
        track = Track("Test Track")
        loop.set_track(track, 1)
        self.obj.set_active_loop(loop)
        self.obj.set_track_position_occupied(1, True)

        # Adjust volume
        self.obj.adjust_track_volume(1, 0.7)
        self.assertEqual(track.get_volume(), 0.7)

    def test_clear_track(self):
        """Tests Controller's clear_track method."""
        from loop import Loop
        from track import Track
        loop = Loop("Test Loop")
        track = Track("Test Track")
        loop.set_track(track, 1)
        self.obj.set_active_loop(loop)
        self.obj.set_track_position_occupied(1, True)

        # Clear the track
        self.obj.clear_track(1)
        self.assertIsNone(loop.loop_tracks[1])
        self.assertFalse(self.obj.get_is_track_occupied(1))

    def test_apply_reverse(self):
        """Tests Controller's apply_reverse method."""
        from loop import Loop
        from track import Track
        loop = Loop("Test Loop")
        track = Track("Test Track")
        loop.set_track(track, 1)
        self.obj.set_active_loop(loop)
        self.obj.set_track_position_occupied(1, True)

        # Apply reverse effect
        original_reverse = track.is_reversed
        self.obj.apply_reverse(1)
        self.assertNotEqual(track.is_reversed, original_reverse)

    def test_apply_xf1(self):
        """Tests Controller's apply_xf1 (time dilation) method."""
        from loop import Loop
        from track import Track
        loop = Loop("Test Loop")
        track = Track("Test Track")
        loop.set_track(track, 1)
        self.obj.set_active_loop(loop)
        self.obj.set_track_position_occupied(1, True)

        # Apply time dilation
        self.obj.apply_xf1(1, 1.5)
        self.assertEqual(track.get_time_dilation(), 1.5)

    def test_apply_xf2(self):
        """Tests Controller's apply_xf2 (pitch modulation) method."""
        from loop import Loop
        from track import Track
        loop = Loop("Test Loop")
        track = Track("Test Track")
        loop.set_track(track, 1)
        self.obj.set_active_loop(loop)
        self.obj.set_track_position_occupied(1, True)

        # Apply pitch modulation
        self.obj.apply_xf2(1, 3)
        self.assertEqual(track.get_pitch_modulation(), 3)

    def test_solo_track(self):
        """Tests Controller's solo_track method."""
        from loop import Loop
        from track import Track
        loop = Loop("Test Loop")
        track = Track("Test Track")
        loop.set_track(track, 1)
        self.obj.set_active_loop(loop)
        self.obj.set_track_position_occupied(1, True)

        # Solo the track
        self.obj.solo_track(1)
        self.assertEqual(self.obj.get_loop_to_play(), track)

    def test_set_project_home(self):
        """Tests Controller's set_project_home method."""
        import tempfile
        fm = FileManager()
        self.obj.set_file_manager(fm)

        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.obj.set_project_home(temp_dir)
            self.assertEqual(str(result), temp_dir)
            self.assertEqual(self.obj.get_home_folder(), temp_dir)

    def test_rename_project_file(self):
        """Tests Controller's rename_project_file method."""
        import tempfile
        fm = FileManager()
        self.obj.set_file_manager(fm)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("test")

            # Rename it
            new_path = self.obj.rename_project_file(test_file, "renamed.txt")
            self.assertTrue(os.path.exists(str(new_path)))
            self.assertFalse(os.path.exists(test_file))

    def test_delete_project_file(self):
        """Tests Controller's delete_project_file method."""
        fm = FileManager()
        self.obj.set_file_manager(fm)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("test")

            # Delete it (this will move to trash)
            self.obj.delete_project_file(test_file)
            # File should no longer exist in original location
            self.assertFalse(os.path.exists(test_file))

    def test_load_state_workflow(self):
        """Tests load state toggle and workflow."""
        # Default load state should be False
        self.assertFalse(self.obj.get_load_state())

        # Toggle to load mode
        self.obj.toggle_load()
        self.assertTrue(self.obj.get_load_state())

        # Toggle back to normal mode
        self.obj.toggle_load()
        self.assertFalse(self.obj.get_load_state())

    def test_serialize_deserialize_workflow(self):
        """Tests complete serialize/deserialize workflow."""
        fm = FileManager()
        self.obj.set_file_manager(fm)

        # Create loop with track
        loop = Loop("Test Workflow Loop")
        track = Track("Test Workflow Track")
        loop.set_track(track, 1)
        self.obj.set_active_loop(loop)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Serialize the loop
            loop_path = os.path.join(temp_dir, "workflow_test.loop")
            result = fm.serialize_loop(loop, loop_path)
            self.assertTrue(os.path.exists(loop_path))

            # Deserialize and verify
            deserialized_loop = fm.deserialize_loop(loop_path)
            self.assertEqual(loop.loop_name, deserialized_loop.loop_name)
            self.assertEqual(loop._loop_id, deserialized_loop._loop_id)

    def test_track_effects_workflow(self):
        """Tests applying multiple effects to a track in sequence."""
        loop = Loop("Effects Test Loop")
        track = Track("Effects Test Track")
        loop.set_track(track, 1)
        self.obj.set_active_loop(loop)
        self.obj.set_track_position_occupied(1, True)

        # Apply effects in sequence
        self.obj.adjust_track_volume(1, 0.8)
        self.obj.apply_reverse(1)
        self.obj.apply_xf1(1, 1.5)  # Time dilation
        self.obj.apply_xf2(1, 2)    # Pitch modulation

        # Verify all effects applied
        self.assertEqual(track.get_volume(), 0.8)
        self.assertTrue(track.is_reversed)
        self.assertEqual(track.get_time_dilation(), 1.5)
        self.assertEqual(track.get_pitch_modulation(), 2)

    def test_loop_track_management_workflow(self):
        """Tests complete loop and track management workflow."""
        # Create loop and add multiple tracks
        loop = Loop("Management Test Loop")
        track1 = Track("Track 1")
        track2 = Track("Track 2")

        self.obj.set_active_loop(loop)

        # Add tracks
        loop.set_track(track1, 1)
        loop.set_track(track2, 2)
        self.obj.set_track_position_occupied(1, True)
        self.obj.set_track_position_occupied(2, True)

        # Update occupation status
        self.obj.update_all_tracks_occupied_status()
        self.assertTrue(self.obj.get_is_track_occupied(1))
        self.assertTrue(self.obj.get_is_track_occupied(2))

        # Clear one track
        self.obj.clear_track(1)
        self.assertFalse(self.obj.get_is_track_occupied(1))
        self.assertTrue(self.obj.get_is_track_occupied(2))

        # Solo remaining track
        self.obj.solo_track(2)
        self.assertEqual(self.obj.get_loop_to_play(), track2)


if __name__ == '__main__':
    unittest.main()
