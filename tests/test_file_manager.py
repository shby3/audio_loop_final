import os
import unittest
from file_manager import FileManager
import tempfile
from track import Track

"""
+++------------------------------------------------------------------------+++
Defines a Test suite for the File Manager class and all related methods.
Generally, this file manager class is responsible for anything file / folder /
directory related. It hands the content list and any processes for
serialization and deserialization in track and loop.

Written by: Michelle Mann
+++------------------------------------------------------------------------+++
"""


class TestFileManager(unittest.TestCase):
    """
    Description: Tests all functionalities of FileManager component including
    serialization, deserialization, and file management operations.
    Methods:
        - test_serialize_track(): Tests Track object serialization to .track
                                        file
        - test_deserialize_track(): Tests Track object deserialization from
                                        .track file
        - test_serialize_loop(): Tests Loop object serialization to .loop file
        - test_deserialize_loop(): Tests Loop object deserialization from
                                        .loop file
        - test_set_home_directory(): Tests project directory structure creation
        - test_rename_file(): Tests file renaming functionality
        - test_delete_file(): Tests safe file deletion functionality
    """

    def setUp(self):
        self.fm = FileManager()

    def test_serialize_track(self):
        """Tests FileManager's serialize_track method."""

        track = Track("Test Track")

        with tempfile.TemporaryDirectory() as temp_dir:
            track_path = os.path.join(temp_dir, "test_track.track")
            result = self.fm.serialize_track(track, track_path)

            self.assertTrue(os.path.exists(track_path))
            self.assertEqual(str(result), track_path)

    def test_set_home_directory(self):
        """Tests FileManager's set_home_directory method."""

        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.fm.set_home_directory(temp_dir)

            # Check that directories were created
            self.assertTrue((result / "Tracks").exists())
            self.assertTrue((result / "Loops").exists())
            self.assertTrue((result / ".hidden" / ".recordings").exists())
            self.assertTrue((result / ".hidden" / ".waveform_images").exists())

    def test_rename_file(self):
        """Tests FileManager's rename_file method."""

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_file = os.path.join(temp_dir, "original.txt")
            with open(test_file, 'w') as f:
                f.write("test")

            # Rename it
            new_path = self.fm.rename_file(test_file, "renamed.txt")

            self.assertTrue(os.path.exists(str(new_path)))
            self.assertFalse(os.path.exists(test_file))

    def test_deserialize_track(self):
        """Tests FileManager's deserialize_track method."""
        track = Track("Test Track")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Serialize first
            track_path = os.path.join(temp_dir, "test_track.track")
            self.fm.serialize_track(track, track_path)

            # Then deserialize
            deserialized_track = self.fm.deserialize_track(track_path)

            self.assertEqual(track.track_name, deserialized_track.track_name)
            self.assertEqual(track.track_id, deserialized_track.track_id)

    def test_serialize_loop(self):
        """Tests FileManager's serialize_loop method."""
        from loop import Loop
        loop = Loop("Test Loop")

        with tempfile.TemporaryDirectory() as temp_dir:
            loop_path = os.path.join(temp_dir, "test_loop.loop")
            result = self.fm.serialize_loop(loop, loop_path)

            self.assertTrue(os.path.exists(loop_path))
            self.assertEqual(str(result), loop_path)

    def test_deserialize_loop(self):
        """Tests FileManager's deserialize_loop method."""
        from loop import Loop
        loop = Loop("Test Loop")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Serialize first
            loop_path = os.path.join(temp_dir, "test_loop.loop")
            self.fm.serialize_loop(loop, loop_path)

            # Then deserialize
            deserialized_loop = self.fm.deserialize_loop(loop_path)

            self.assertEqual(loop.loop_name, deserialized_loop.loop_name)
            self.assertEqual(loop._loop_id, deserialized_loop._loop_id)

    def test_delete_file(self):
        """Tests FileManager's delete_file method."""

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_file = os.path.join(temp_dir, "to_delete.txt")
            with open(test_file, 'w') as f:
                f.write("test")

            # Delete it
            self.fm.delete_file(test_file)

            # Should no longer exist
            self.assertFalse(os.path.exists(test_file))


if __name__ == '__main__':
    unittest.main()
