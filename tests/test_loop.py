import unittest
from loop import Loop
from track import Track

"""
+++------------------------------------------------------------------------+++
Defines a Test suite for the Loop class and all related methods.
Generally, this loop class is responsible for all aspects of the data class
called loop.

Written by: Michelle Mann
+++------------------------------------------------------------------------+++
"""


class TestLoop(unittest.TestCase):
    """
    Description: Tests all functionalities of Loop component including
    track management, selection state, and loop operations.
    Methods:
        - test_loop_creation(): Tests Loop object initialization and default
                                        values
        - test_set_track(): Tests adding tracks to loop positions
        - test_remove_track(): Tests removing tracks from loop positions
        - test_toggle_selection(): Tests loop selection state toggling
    """

    def setUp(self):
        self.loop = Loop("Test Loop")

    def test_loop_creation(self):
        """Tests Loop object creation."""
        self.assertEqual(self.loop.loop_name, "Test Loop")
        self.assertFalse(self.loop.is_selected)
        self.assertTrue(self.loop.is_empty())

    def test_set_track(self):
        """Tests Loop's set_track method."""
        track = Track("Test Track")

        self.loop.set_track(track, 1)
        self.assertEqual(self.loop.loop_tracks[1], track)
        self.assertFalse(self.loop.is_empty())

    def test_remove_track(self):
        """Tests Loop's remove_track method."""
        track = Track("Test Track")

        self.loop.set_track(track, 1)
        self.loop.remove_track(1)
        self.assertIsNone(self.loop.loop_tracks[1])
        self.assertTrue(self.loop.is_empty())

    def test_toggle_selection(self):
        """Tests Loop's toggle_selection method."""
        self.assertFalse(self.loop.is_selected)
        self.loop.toggle_selection()
        self.assertTrue(self.loop.is_selected)
        self.loop.toggle_selection()
        self.assertFalse(self.loop.is_selected)


if __name__ == '__main__':
    unittest.main()
