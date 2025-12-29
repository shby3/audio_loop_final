"""
+++------------------------------------------------------------------------+++
Creation of the methods associated with serialization
and deserialization for tracks and loops.
+++------------------------------------------------------------------------+++
"""


import json
import re

from .loop import Loop
from .track import Track
from pathlib import Path


class FileManager:
    """
    Description: Represents the file manager handling file structures for our
    app. The File Manager reads directly from the data structures associated
    with storing, reading, writing, serializing and deserializing our files.
    Args:
        - serialize_loop (loop: Obj): Takes a loop object and stores as a .loop
                                        JSON readable file in computer memory
                                        (not local memory).
        - deserialize_loop (path: str): Takes a file path for a .loop file and
                                        maps the associated JSON object to a
                                        Loop object.
    """

    def serialize_loop(self, loop: Loop, path: str = None) -> Path:
        """
        Description: Writes a Loop object to a .loop extension. This file can
        then be accessed from a file browser as needed. Stored as a
        JSON file until passed into a dedicated Loop object to keep
        human-readable.

        Args:
            - loop (Loop): A Loop dataclass structure.
            - path (str): Optional file path. If not provided, uses loop name.

        Returns:
            - A dedicated file path mapped to a dataclass storage location.
        """
        if path is None:
            invalid_chars = r'[\\/:*?"|<>\x00 ]'
            clean_name = re.sub(invalid_chars, '_', loop.loop_name)
            path = f"{loop.project_path}/{clean_name}.loop"
        p = Path(path)

        # Make project directory
        d = Path(loop.project_path)
        d.mkdir(exist_ok=True)

        # Serialize track objects to their file paths or None
        serialized_tracks = {}
        for pos, track in loop.loop_tracks.items():
            track_data = {
                "name": track.track_name,
                "id": track.track_id,
                "filepath": track.track_filepath,
                "project_path": track.project_path,
                "left": track.left,
                "right": track.right
            }
            serialized_tracks[pos] = track_data

        data = {
            "loop_name": loop.loop_name,
            "loop_tracks": serialized_tracks,
            "loop_birth": (loop.loop_birth.isoformat()
                           if hasattr(loop.loop_birth, 'isoformat')
                           else str(loop.loop_birth)),
            "loop_id": loop.loop_id,
            "project_path": loop.project_path,
        }

        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return p

    def deserialize_loop(self, path: str) -> Loop:
        """
        Description: Loads a Loop from a .loop file extension. This file can
        then be accessed via it's loop playback around (either the loop design)
        area or the loop buckets area) as needed. Loop files will deserialize
        as JSON files until loaded, and then will be stored in memory as a Loop
        class object.

        Args:
            - path (): The naming convention (a timestamp) associated with a
                                        file name.

        Returns:
            - A Loop object that can be passed to valid loop readable areas.

        Relationships:
            - Callable from Controller.
        """
        # Gets the file path as a JSON object.
        text = Path(path).read_text(encoding="utf-8")
        data = json.loads(text)

        # Create loop first
        loop = Loop(loop_name=data["loop_name"], project_path=data["project_path"])

        # Maps the loop data - deserialize track paths to Track objects
        loop_dir = Path(path).parent

        for pos, track_data in data["loop_tracks"].items():
            try:
                loop.loop_tracks[int(pos)] = Track(
                    track_filepath=track_data["filepath"],
                    track_name=track_data["name"],
                    project_path=track_data["project_path"],
                    left=float(track_data["left"]),
                    right=float(track_data["right"])
                )
            except FileNotFoundError:
                # For testing: keep track path string if file missing
                loop.loop_tracks[int(pos)] = Track()

        # Use loop_id from JSON if available
        if "loop_id" in data:
            loop.loop_id = data["loop_id"]

        # Handle datetime deserialization
        from datetime import datetime
        if isinstance(data["loop_birth"], str):
            try:
                loop.loop_birth = datetime.fromisoformat(data["loop_birth"])
            except ValueError:
                loop.loop_birth = datetime.now()
        else:
            loop.loop_birth = data["loop_birth"]

        return loop

    def deserialize_track(self, path: str, loop_id: str = None):
        """
        Description: Loads a Track from a .track file.
        Args:
            - path (str): Path to the .track file
            - loop_id (str): The loop_id this track belongs to
        Returns:
            - Track object
        """
        text = Path(path).read_text(encoding="utf-8")
        data = json.loads(text)

        # Create Track object with correct constructor args
        track = Track(
            track_name=data.get("track_name", "New Track"),
            channel_config=data.get("channel_config", 1),
            time_dilation=data.get("time_dilation", 0),
            pitch_modulation=data.get("pitch_modulation", 0)
        )
        
        # Override the auto-generated track_id with the one from file
        track.track_id = data["track_id"]

        # Set additional attributes that aren't in constructor
        track.track_state = data.get("track_state", "STOP")
        track.track_volume = data.get("track_volume", 1.0)
        track.track_birth = data.get("track_birth", track.track_birth)
        track.track_name = data.get("track_name")
        track.track_waveform = data.get("track_waveform")
        track.file_path = path

        return track

    def serialize_track(self, track: Track, path: str = None) -> Path:
        """
        Description: Writes a Track object to a .track file.
        Args:
            - track (Track): A Track object
            - path (str): Optional file path. If not provided, uses track_id
        Returns:
            - Path: The file path where track was saved
        """
        if path is None:
            path = f"{track.track_id}.track"

        p = Path(path)
        data = {
            "track_id": track.track_id,
            "track_name": track.track_name,
            "channel_config": track.channel_config,
            "track_volume": track.track_volume,
            "time_dilation": track.time_dilation,
            "pitch_modulation": track.pitch_modulation,
            "track_birth": (track.track_birth.isoformat()
                            if hasattr(track.track_birth, 'isoformat')
                            else str(track.track_birth))
        }

        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return p

    def setup_project_directories(self, home_path: Path):
        """
        Description: Creates the required project directory structure.
        Args:
            - home_path (Path): Path to the home directory
        Returns:
            - None
        Relationship(s):
            - File structure should look like this:
            <home_dir>:
                - Tracks
                - Loops
                - .hidden:
                    - .samples
                    - .waveform_images
        """

        home_dir = home_path

        # Create Tracks and Loops folders
        tracks_dir = home_dir / "Tracks"
        loops_dir = home_dir / "Loops"
        tracks_dir.mkdir(exist_ok=True)
        loops_dir.mkdir(exist_ok=True)

        # Create hidden folders
        hidden_dir = home_dir / ".hidden"           # Parent of hidden folders.

        # Children of hidden folders
        recordings_dir = hidden_dir / ".samples"
        waveform_images_dir = hidden_dir / ".waveform_images"

        recordings_dir.mkdir(parents=True, exist_ok=True)
        waveform_images_dir.mkdir(parents=True, exist_ok=True)

    def set_home_directory(self, folder_path: str):
        """Sets up project directory structure in specified folder."""
        root = Path(folder_path)
        self.setup_project_directories(root)
        return root

    def rename_file(self, src_path: str, new_name: str):
        """Renames a file or folder."""
        src = Path(src_path)
        dst = src.with_name(new_name.strip())
        if dst.exists() and dst != src:
            raise FileExistsError(f"'{new_name}' already exists")
        src.rename(dst)
        return dst

    def delete_file(self, file_path: str):
        """Deletes a file using send2trash for safe removal."""
        from send2trash import send2trash
        send2trash(str(file_path))
