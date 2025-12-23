import unittest
from track import Track

"""
+++------------------------------------------------------------------------+++
Defines a Test suite for the Track class and all related methods.
Generally, this track class is responsible for all aspects of the data class
called track.

Written by: Michelle Mann
+++------------------------------------------------------------------------+++
"""


class TestTrack(unittest.TestCase):
    """
    Description: Tests all functionalities of Track component including
    audio properties, effects, and track control operations.
    Methods:
        - test_track_creation(): Tests Track object initialization and default
                                        values.
        - test_volume_control(): Tests track volume get/set functionality.
        - test_reverse_control(): Tests track reverse effect toggle.
        - test_pitch_modulation(): Tests pitch modulation get/set
                                        functionality.
        - test_time_dilation(): Tests time dilation get/set functionality.
        - test_track_name(): Tests track name get/set functionality.
    """

    def setUp(self):
        self.track = Track("Test Track")

    def test_track_creation(self):
        """Tests Track object creation."""
        self.assertEqual(self.track.track_name, "Test Track")
        self.assertEqual(self.track.track_volume, 1.0)
        self.assertEqual(self.track.track_state, "STOP")

    def test_volume_control(self):
        """Tests Track volume get/set methods."""
        self.track.set_volume(0.5)
        self.assertEqual(self.track.get_volume(), 0.5)

    def test_reverse_control(self):
        """Tests Track reverse get/set methods."""
        original = self.track.is_reversed
        self.track.set_reverse(not original)
        self.assertNotEqual(self.track.is_reversed, original)

    def test_pitch_modulation(self):
        """Tests Track pitch modulation get/set methods."""
        self.track.set_pitch_modulation(5)
        self.assertEqual(self.track.get_pitch_modulation(), 5)

    def test_time_dilation(self):
        """Tests Track time dilation get/set methods."""
        self.track.set_time_dilation(1.2)
        self.assertEqual(self.track.get_time_dilation(), 1.2)

    def test_track_name(self):
        """Tests Track name get/set methods."""
        self.track.set_track_name("New Name")
        self.assertEqual(self.track.get_track_name(), "New Name")


if __name__ == '__main__':
    unittest.main()
