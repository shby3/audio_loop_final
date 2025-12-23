import os
import unittest
from file_manager import FileManager
from bucket import Bucket, BucketState
import exceptions as e


class TestBucket(unittest.TestCase):
    """
    Description: Tests all functionalities of Bucket component including
    all getter / setter methods.
    Methods:
        - test_bucket_creation: Tests full creation of Bucket() object.
        - test_get_bucket_id: Tests getter method for returning bucket_id
        - test_get_is_bucket_active: Tests getter method for returning if
                                        bucket is active (not empty).
    """
    def setUp(self):
        """
        Sets up Bucket between tests.
        """
        self.obj = Bucket(1)

    def tearDown(self):
        """
        Removes Bucket between tests.
        """
        del self.obj

    def test_bucket_creation(self):
        """
        Tests Bucket's creation - ensuring the initialization works correctly.
        """
        id = self.obj.get_bucket_id()
        active = self.obj.get_is_bucket_active()
        loop = self.obj.get_mapped_loop()
        name = self.obj.get_loop_display_name()
        path = self.obj.get_loop_path()
        state = self.obj.get_bucket_state()
        tracks = self.obj.display_track_indicators()

        self.assertEqual(1, id)
        self.assertEqual(active, False)
        self.assertEqual(loop, None)
        self.assertEqual(name, None)
        self.assertEqual(path, None)
        self.assertEqual(state, BucketState.EMPTY)
        self.assertEqual(tracks, (False, False, False, False, False, False))

        self.assertEqual(Bucket, type(self.obj))

    def test_get_bucket_id(self):
        """
        Tests Bucket's default bucket_id reading.
        [Default id should read as 1]
        """
        id = self.obj.get_bucket_id()
        self.assertEqual(1, id)

    def test_get_is_bucket_active(self):
        """
        Tests Bucket's default is_bucket_active method.
        [Default should read as False -- indicating inactive bucket.]
        """
        active = self.obj.get_is_bucket_active()
        self.assertFalse(active)

    def test_set_is_bucket_active(self):
        """
        Tests Bucket's ability to set alternative states to is_bucket_active
        parameter.
        [Default will test as False, then True, then False again.]
        """
        active = self.obj.get_is_bucket_active()
        self.assertFalse(active)

        self.obj.set_is_bucket_active()
        active = self.obj.get_is_bucket_active()
        self.assertTrue(active)

        self.obj.set_is_bucket_active()
        active = self.obj.get_is_bucket_active()
        self.assertFalse(active)

    def test_get_set_mapped_loop(self):
        """
        Tests Bucket's ability to return associated mapped loop. This
        vicariously tests get/set for loop_display_name, loop_path
        [Default will return None, then Loop object once set.]
        """
        # Default: no mapped loop
        loop = self.obj.get_mapped_loop()
        self.assertIsNone(loop)

        # Build loop path
        base_dir = os.path.dirname(__file__)
        loop_path = os.path.join(base_dir, "test_cases",
                                 "Loop_20250115214530.loop")
        loop_path = os.path.abspath(loop_path)

        # File manager is required to deserialize loop.
        fm = FileManager()
        expected_loop = fm.deserialize_loop(loop_path)

        # Set mapped loop on the bucket (by path)
        self.obj.set_mapped_loop(loop_path)
        actual_loop = self.obj.get_mapped_loop()

        # Compare loops
        self.assertEqual(expected_loop.loop_name, actual_loop.loop_name)
        self.assertEqual(expected_loop.loop_tracks, actual_loop.loop_tracks)
        self.assertEqual(expected_loop.loop_length, actual_loop.loop_length)
        self.assertEqual(expected_loop.loop_elapsed_secs,
                         actual_loop.loop_elapsed_secs)

        # Bucket’s display name & path should match the mapped loop
        self.assertEqual(self.obj.get_loop_display_name(),
                         expected_loop.get_loop_display_name())

        # Path stored on the bucket should be the file path we used
        self.assertEqual(self.obj.get_loop_path(), expected_loop.get_loop_id())

        # Track indicators: tuple of booleans based on loop_tracks
        tracks_filled = tuple(
            expected_loop.loop_tracks[pos] is not None
            for pos in sorted(expected_loop.loop_tracks)
        )
        self.assertEqual(tracks_filled, self.obj.display_track_indicators())

    def test_clear_bucket(self):
        """
        Tests that Bucket.clear_bucket() restores the bucket
        to its original, empty state.
        [Sets values on default, then clears and tests.]
        """

        # Paints bucket with fields that aren't defaults.
        self.obj.is_bucket_active = True
        self.obj.mapped_loop = "dummy_loop_object"
        self.obj.loop_display_name = "My Loop"
        self.obj.loop_path = "path/to/loop.loop"
        self.obj.bucket_state = BucketState.PLAYING
        self.obj.is_track_filled = {
            1: True,
            2: True,
            3: False,
            4: True,
            5: False,
            6: True,
        }

        self.obj.clear_bucket()

        # Expectation is that all parameters should be reset.
        self.assertFalse(self.obj.get_is_bucket_active())
        self.assertIsNone(self.obj.get_mapped_loop())
        self.assertIsNone(self.obj.get_loop_display_name())
        self.assertIsNone(self.obj.get_loop_path())
        self.assertEqual(self.obj.get_bucket_state(), BucketState.EMPTY)

        # Track indicators all reset to False
        expected_tracks = {
            1: False,
            2: False,
            3: False,
            4: False,
            5: False,
            6: False
        }

        self.assertEqual(self.obj.is_track_filled, expected_tracks)

    def test_bucket_state_empty_to_playing(self):
        """
        Tests that we can update the bucket set from empty to playing and that
        the bucket reads as playing afterwards.
        [Defaults to EMPTY, test should read as PLAYING]
        """
        self.obj._mark_playing()
        self.assertEqual(self.obj.get_bucket_state(), BucketState.PLAYING)

        self.obj._mark_paused()
        self.assertEqual(self.obj.get_bucket_state(), BucketState.PAUSED)

        self.obj._mark_stopped()
        self.assertEqual(self.obj.get_bucket_state(), BucketState.STOPPED)

        self.obj._mark_empty()
        self.assertEqual(self.obj.get_bucket_state(), BucketState.EMPTY)

    def test_set_bucket_state_valid_transition(self):
        """
        Tests that set_bucket_state should raise InvalidState if the new state
        is the same as the old state.
        [Defaults to EMPTY state]
        """
        # Start in EMPTY by default
        with self.assertRaises(e.InvalidState):
            self.obj._mark_empty()

        # Move to PLAYING, then try to set PLAYING again
        self.obj._mark_playing()
        with self.assertRaises(e.InvalidState):
            self.obj._mark_playing()

    def test_set_bucket_state_type_check(self):
        """
        set_bucket_state should only accept BucketState values.
        """
        with self.assertRaises(TypeError):
            self.obj.set_bucket_state("playing")

        with self.assertRaises(TypeError):
            self.obj.set_bucket_state(123)


if __name__ == "__main__":
    unittest.main()
