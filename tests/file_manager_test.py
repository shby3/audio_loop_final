"""
+++------------------------------------------------------------------------+++
This is a rudimentary GUI built exclusively to test serialization and
deserialization functions for Loop / Track. This is not something we will use
actively in the desktop application itself and is the product of an AI prompt:

Prompt Link: https://chatgpt.com/share/691d4ccd-6040-8006-8b0f-2cecf4c53014
Prompt Provided on 11/18/2025

Written by: ChatGPT & Michelle Mann
+++------------------------------------------------------------------------+++
"""
import sys
import os
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# noqa: E402 - imports after sys.path modification
from file_manager import FileManager  # noqa: E402
from loop import Loop  # noqa: E402

# -------------------------------------------------------------------
# GUI App
# -------------------------------------------------------------------


class SerializationTestApp(tk.Tk):
    def __init__(self, folder: str = "data"):
        super().__init__()
        self.title("Serialization / Deserialization Test")
        self.geometry("600x400")

        # Where JSON files live
        self.folder = Path(folder)
        self.folder.mkdir(exist_ok=True)

        # In-memory object (after deserialization)
        self.current_obj: Loop | None = None
        self.current_filename: Path | None = None

        self.fm = FileManager()

        self._build_ui()
        self._refresh_file_list()

    # ---------------- UI CONSTRUCTION ----------------

    def _build_ui(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left: list of JSON files
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(left_frame, text="Loop files in folder").pack(anchor="w")

        self.file_listbox = tk.Listbox(left_frame, width=30, height=20)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.Y)

        scrollbar = ttk.Scrollbar(left_frame, orient="vertical",
                                  command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        # Right: buttons + details
        right_frame = ttk.Frame(main_frame, padding=(10, 0, 0, 0))
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X)

        self.folder_btn = ttk.Button(
            button_frame, text="Choose Folder", command=self.choose_folder
        )
        self.folder_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.deserialize_btn = ttk.Button(
            button_frame, text="Deserialize", command=self.on_deserialize
        )
        self.deserialize_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.serialize_btn = ttk.Button(
            button_frame, text="Serialize", command=self.on_serialize
        )
        self.serialize_btn.pack(side=tk.LEFT)

        # Status label
        self.status_var = tk.StringVar(value="No object in memory")
        status_label = ttk.Label(right_frame, textvariable=self.status_var)
        status_label.pack(anchor="w", pady=(5, 5))

        # Text area to show object data
        ttk.Label(right_frame,
                  text="Current object representation:").pack(anchor="w")

        self.obj_text = tk.Text(right_frame, height=15)
        self.obj_text.pack(fill=tk.BOTH, expand=True)

    # ---------------- FILE LIST HANDLING ----------------

    def _refresh_file_list(self):
        self.file_listbox.delete(0, tk.END)
        # Look for loop files in Loops subfolder first, then current folder
        loops_dir = self.folder / "Loops"
        if loops_dir.exists():
            files = sorted(loops_dir.glob("*.loop"))
        else:
            files = sorted(self.folder.glob("*.loop"))
        for f in files:
            self.file_listbox.insert(tk.END, f.name)

    def _get_selected_file(self) -> Path | None:
        selection = self.file_listbox.curselection()
        if not selection:
            return None
        filename = self.file_listbox.get(selection[0])
        # Look in Loops subfolder first, then current folder
        loops_dir = self.folder / "Loops"
        if loops_dir.exists() and (loops_dir / filename).exists():
            return loops_dir / filename
        else:
            return self.folder / filename

    # ---------------- BUTTON HANDLERS ----------------

    def choose_folder(self):
        """Allow user to choose a different folder."""
        folder = filedialog.askdirectory(
            title="Choose folder containing loop files",
            initialdir=str(self.folder)
        )
        if folder:
            self.folder = Path(folder)
            self._refresh_file_list()
            self.status_var.set(f"Folder: {self.folder}")

    def on_deserialize(self):
        """Load JSON from selected file and create a Python object."""
        file_path = self._get_selected_file()
        if not file_path:
            messagebox.showwarning("No selection",
                                   "Please select a loop file first.")
            return

        # Validate file exists before deserializing
        if not file_path.exists():
            messagebox.showerror("File Error", "Selected file does not exist.")
            return

        try:
            obj = self.fm.deserialize_loop(str(file_path))
        except Exception as e:
            messagebox.showerror("Deserialization error", str(e))
            return

        self.current_obj = obj
        self.current_filename = file_path

        self._update_obj_view()
        self.status_var.set(f"Deserialized: {file_path.name}")

    def on_serialize(self):
        """
        Serialize the current object back to JSON, write it to disk,
        and then drop the in-memory reference.
        """
        if self.current_obj is None:
            messagebox.showwarning("No object", "Nothing to serialize.")
            return

        if self.current_filename is None:
            # Fallback: create a default filename if none is known
            self.current_filename = self.folder / "output.loop"

        try:
            self.fm.serialize_loop(self.current_obj,
                                   str(self.current_filename))
        except Exception as e:
            messagebox.showerror("Serialization error", str(e))
            return

        # "Delete the copy of the item in memory"
        self.current_obj = None
        self.current_filename = None

        self._update_obj_view()
        self.status_var.set("Object serialized and removed from memory")

    # ---------------- UI HELPERS ----------------

    def _update_obj_view(self):
        self.obj_text.delete("1.0", tk.END)
        if self.current_obj is None:
            self.obj_text.insert(tk.END, "<no object in memory>\n")
        else:
            self.obj_text.insert(tk.END, repr(self.current_obj))


if __name__ == "__main__":
    app = SerializationTestApp(folder="data")
    app.mainloop()
