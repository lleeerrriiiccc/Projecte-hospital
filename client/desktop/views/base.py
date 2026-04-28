from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class BaseView(ttk.Frame):
    """Base class for all desktop screens with shared navigation state."""

    route = "base"

    def __init__(self, master, app_state, navigate, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.app_state = app_state
        self.navigate = navigate

    def on_show(self):
        """Hook called whenever the view becomes visible."""
        pass

    def clear_children(self):
        """Utility to rebuild dynamic sections without recreating the whole view."""
        for child in self.winfo_children():
            child.destroy()
