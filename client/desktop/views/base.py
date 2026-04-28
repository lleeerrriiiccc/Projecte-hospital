import datetime
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

    def clear_tree(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def clear_text_widget(self, text_widget):
        text_widget.configure(state="normal")
        text_widget.delete("1.0", tk.END)

    def get_entry_values(self, entries):
        values = {}
        for key, entry in entries.items():
            values[key] = entry.get().strip()
        return values

    def reset_entries(self, entries, defaults=None):
        defaults = defaults or {}
        for key, entry in entries.items():
            entry.delete(0, tk.END)
            if key in defaults:
                entry.insert(0, defaults[key])

    def today_iso(self):
        return datetime.date.today().isoformat()

    def parse_iso_date(self, value, error_message):
        try:
            return datetime.datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError(error_message) from exc

    def build_options_map(self, rows, id_keys, label_keys):
        mapping = {}

        for row in rows:
            option_id = None
            option_label = None

            if isinstance(row, dict):
                for key in id_keys:
                    value = row.get(key)
                    if value not in (None, ""):
                        option_id = value
                        break

                for key in label_keys:
                    value = row.get(key)
                    if value not in (None, ""):
                        option_label = value
                        break
            elif isinstance(row, (list, tuple)) and len(row) >= 2:
                option_id, option_label = row[0], row[1]

            if option_id is None or not option_label:
                continue

            mapping[str(option_id)] = str(option_label)

        return mapping

    def build_combo_values(self, mapping):
        values = []
        for option_id, label in mapping.items():
            values.append(f"{option_id} - {label}")
        return values

    def split_combo_value(self, value):
        return str(value).split(" - ", 1)[0].strip()
