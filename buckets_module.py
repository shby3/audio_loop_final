"""
+++------------------------------------------------------------------------+++
Defines a BucketsModule class for managing multiple bucket objects.
Generally, this module manages a collection of buckets for immediate
loop playback functionality.

Written by: Michelle Mann
+++------------------------------------------------------------------------+++
"""

from bucket import Bucket, BucketState
from loop import Loop


class BucketsModule:
    """
    Description: Manages a collection of bucket objects for loop playback. The
    active Bucket Module holds 10 given buckets for immediate playback.

    Args:
        - buckets (dict): Dictionary of bucket objects indexed by bucket_id

    Methods:
        - get_bucket(bucket_id): Returns bucket object by ID
        - load_bucket(loop, bucket_id): Loads loop into specified bucket
        - get_bucket_loop(bucket_id): Returns loop from specified bucket
        - clear_bucket(bucket_id): Clears specified bucket
        - get_all_buckets(): Returns all bucket objects
        - pause_bucket(bucket_id): Pauses bucket playback
        - play_bucket_state(bucket_id): Sets bucket to playing state
        - stop_bucket(bucket_id): Stops bucket playback
        - get_last_touched_bucket(): Returns last touched bucket ID
    """

    def __init__(self, num_buckets=10):
        """
        Initializes buckets module with specified number of buckets.
        Args:
            - num_buckets (int): Number of buckets to create (default 10)
        """
        self.buckets = {}
        self.last_touched_bucket = None
        for i in range(1, num_buckets + 1):
            self.buckets[i] = Bucket(i)

    def get_bucket(self, bucket_id: int) -> Bucket:
        """
        Description: Returns bucket object by ID.
        Args:
            - bucket_id (int): ID of bucket to retrieve
        Returns:
            - Bucket: Bucket object
        """
        return self.buckets.get(bucket_id)

    def load_bucket(self, loop: Loop, bucket_id: int) -> None:
        """
        Description: Loads loop into specified bucket.
        Args:
            - loop (Loop): Loop object to load
            - bucket_id (int): ID of bucket to load into
        Returns:
            - None
            - [Action]: Sets Bucket state to full and maps all bucket features
            to bucket location.
        """
        bucket = self.get_bucket(bucket_id)

        if bucket:
            # Clear bucket first if it has content
            if bucket.get_is_bucket_active():
                bucket.clear_bucket()

            # Assign loop to bucket
            bucket.set_mapped_loop(loop)
            bucket.set_is_bucket_active()

    def get_bucket_loop(self, bucket_id: int) -> Loop:
        """
        Description: Returns loop from specified bucket.
        Args:
            - bucket_id (int): ID of bucket
        Returns:
            - Loop: Loop object from bucket, or None if empty
        """
        bucket = self.get_bucket(bucket_id)

        if bucket and bucket.get_is_bucket_active():
            return bucket.get_mapped_loop()
        return None

    def clear_bucket(self, bucket_id: int) -> None:
        """
        Description: Clears specified bucket.
        Args:
            - bucket_id (int): ID of bucket to clear
        Returns:
            - None
            - [Action]: Toggles the bucket state to empty.
        """
        bucket = self.get_bucket(bucket_id)

        if bucket:
            bucket.clear_bucket()

    def set_bucket_state(self, bucket_id: int, state: BucketState) -> None:
        """
        Description: Sets state of specified bucket.
        Args:
            - bucket_id (int): ID of bucket
            - state (BucketState): State to set
        Returns:
            - None
            - [Action]: Sets the state of the bucket in bucket_id to
            BucketState
        """
        bucket = self.get_bucket(bucket_id)

        if bucket:
            bucket.set_bucket_state(state)
            self.last_touched_bucket = bucket_id

    def pause_bucket(self, bucket_id: int) -> None:
        """
        Description: Pauses specified bucket.
        Args:
            - bucket_id (int): ID of bucket to pause
        Returns:
            - None
            - [Action]: Sets bucket at bucket_id to PAUSED.
        """
        if self.get_bucket(bucket_id) and \
                self.get_bucket(bucket_id).get_is_bucket_active():
            self.set_bucket_state(bucket_id, BucketState.PAUSED)

    def play_bucket_state(self, bucket_id: int) -> None:
        """
        Description: Sets bucket to playing state.
        Args:
            - bucket_id (int): ID of bucket to play
        Returns:
            - None
            - [Action]: Sets bucket at bucket_id to PLAYING
        """
        if self.get_bucket(bucket_id) and \
                self.get_bucket(bucket_id).get_is_bucket_active():
            self.set_bucket_state(bucket_id, BucketState.PLAYING)

    def stop_bucket(self, bucket_id: int) -> None:
        """
        Description: Stops specified bucket.
        Args:
            - bucket_id (int): ID of bucket to stop
        Returns:
            - None
            - [Action]: Sets bucket at bucket_id to STOPPED
        """
        if self.get_bucket(bucket_id) and \
                self.get_bucket(bucket_id).get_is_bucket_active():
            self.set_bucket_state(bucket_id, BucketState.STOPPED)

    def get_last_touched_bucket(self):
        """
        Description: Returns the ID of the last touched bucket.
        Args:
            - None
        Returns:
            - int: ID of last touched bucket, or None if none touched
        """
        return self.last_touched_bucket
