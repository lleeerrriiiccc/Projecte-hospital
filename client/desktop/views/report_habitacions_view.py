from __future__ import annotations

import datetime
import tkinter as tk
from tkinter import ttk

from ..api_client import ApiError
from .base import BaseView


class ReportHabitacionsView(BaseView):
    route = "report_habitacions"

    def __init__(self, master, app_state, navigate, *args, **kwargs):
        super().__init__(master, app_state, navigate, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        card = ttk.Frame(self, style="Card.TFrame", padding=20)
        card.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        card.columnconfigure(0, weight=1)
        card.rowconfigure(4, weight=1)
        card.rowconfigure(6, weight=1)

        ttk.Label(card, text="Informe d'Habitacions", style="Title.TLabel").grid(row=0, column=0, sticky="w")

        controls = ttk.Frame(card)
        controls.grid(row=1, column=0, sticky="we", pady=(10, 8))

        ttk.Label(controls, text="Habitacio").grid(row=0, column=0, sticky="w")
        self.room_combo = ttk.Combobox(controls, state="readonly", width=16)
        self.room_combo.grid(row=0, column=1, sticky="w", padx=(8, 14))

        ttk.Label(controls, text="Mes (YYYY-MM)").grid(row=0, column=2, sticky="w")
        self.month_entry = ttk.Entry(controls, width=12)
        self.month_entry.grid(row=0, column=3, sticky="w", padx=(8, 8))
        self.month_entry.insert(0, datetime.date.today().strftime("%Y-%m"))

        ttk.Button(controls, text="Cargar", style="Primary.TButton", command=self._load_data).grid(row=0, column=4, sticky="w")
        ttk.Button(controls, text="Volver", command=lambda: self.navigate("home")).grid(row=0, column=5, sticky="w", padx=(8, 0))

        self.message_var = tk.StringVar(value="Selecciona habitacio y mes para consultar ocupacion.")
        ttk.Label(card, textvariable=self.message_var, style="Muted.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 8))

        self.summary_var = tk.StringVar(value="")
        ttk.Label(card, textvariable=self.summary_var, style="Muted.TLabel").grid(row=3, column=0, sticky="w", pady=(0, 8))

        ttk.Label(card, text="Calendari d'ocupacio", style="Muted.TLabel").grid(row=4, column=0, sticky="w", pady=(0, 6))

        self.calendar_text = tk.Text(
            card,
            height=14,
            wrap="none",
            relief="solid",
            borderwidth=1,
            font=("Courier New", 10),
            background="#ffffff",
        )
        self.calendar_text.grid(row=5, column=0, sticky="nsew")

        cal_scroll = ttk.Scrollbar(card, orient="vertical", command=self.calendar_text.yview)
        cal_scroll.grid(row=5, column=1, sticky="ns")
        self.calendar_text.configure(yscrollcommand=cal_scroll.set)

        cols = ("data_inici", "data_fi", "pacient")
        self.tree = ttk.Treeview(card, columns=cols, show="headings", height=8)
        self.tree.heading("data_inici", text="Data inici")
        self.tree.heading("data_fi", text="Data fi")
        self.tree.heading("pacient", text="Pacient")
        self.tree.column("data_inici", width=120, anchor="center")
        self.tree.column("data_fi", width=120, anchor="center")
        self.tree.column("pacient", width=460, anchor="w")
        self.tree.grid(row=6, column=0, sticky="nsew", pady=(8, 0))

        scrollbar = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=6, column=1, sticky="ns", pady=(8, 0))
        self.tree.configure(yscrollcommand=scrollbar.set)

    def _to_date(self, value):
        try:
            return datetime.datetime.strptime(str(value), "%Y-%m-%d").date()
        except ValueError:
            return None

    def _occupants_for_day(self, day_date, rows):
        occupants = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            start = self._to_date(row.get("data_inici"))
            end = self._to_date(row.get("data_fi"))
            if start is None or end is None:
                continue
            if start <= day_date <= end:
                occupants.append(str(row.get("pacient") or "pacient"))
        return occupants

    def _render_calendar(self, month_value, rows):
        self.calendar_text.configure(state="normal")
        self.calendar_text.delete("1.0", tk.END)

        year, month = month_value.split("-")
        year_int = int(year)
        month_int = int(month)

        first = datetime.date(year_int, month_int, 1)
        if month_int == 12:
            next_month = datetime.date(year_int + 1, 1, 1)
        else:
            next_month = datetime.date(year_int, month_int + 1, 1)

        last_day = (next_month - datetime.timedelta(days=1)).day
        offset = first.weekday()

        self.calendar_text.insert(tk.END, "Dl  Dt  Dc  Dj  Dv  Ds  Dg\n")
        self.calendar_text.insert(tk.END, "-" * 48 + "\n")

        current_col = 0
        if offset > 0:
            self.calendar_text.insert(tk.END, "    " * offset)
            current_col = offset

        for day in range(1, last_day + 1):
            day_date = datetime.date(year_int, month_int, day)
            occupants = self._occupants_for_day(day_date, rows)
            marker = "*" if occupants else " "
            token = f"{day:02d}{marker} "
            self.calendar_text.insert(tk.END, token)
            current_col += 1

            if current_col == 7:
                if occupants:
                    pass
                self.calendar_text.insert(tk.END, "\n")
                current_col = 0

        if current_col != 0:
            self.calendar_text.insert(tk.END, "\n")

        self.calendar_text.insert(tk.END, "\nLlegenda: * dia ocupat\n\n")
        for day in range(1, last_day + 1):
            day_date = datetime.date(year_int, month_int, day)
            occupants = self._occupants_for_day(day_date, rows)
            if occupants:
                self.calendar_text.insert(tk.END, f"{day:02d}: {', '.join(occupants)}\n")

        self.calendar_text.configure(state="disabled")

    def _load_rooms(self):
        payload = self.app_state["api"].get_habitacions()
        rows = payload.get("data") or []
        values = []
        for row in rows:
            if isinstance(row, dict):
                room = row.get("num_habitacio")
            elif isinstance(row, (list, tuple)) and row:
                room = row[0]
            else:
                room = None
            if room is not None:
                values.append(str(room))

        self.room_combo.configure(values=values)
        if values and not self.room_combo.get():
            self.room_combo.set(values[0])

    def _month_matches(self, row, month_prefix):
        if not month_prefix:
            return True
        start = str(row.get("data_inici") or "")
        end = str(row.get("data_fi") or "")
        return start.startswith(month_prefix) or end.startswith(month_prefix)

    def _load_data(self):
        room_value = self.room_combo.get().strip()
        month_value = self.month_entry.get().strip()

        if not room_value:
            self.message_var.set("Selecciona una habitacio.")
            return

        if not month_value:
            self.message_var.set("Selecciona un mes.")
            return

        if month_value:
            try:
                datetime.datetime.strptime(month_value + "-01", "%Y-%m-%d")
            except ValueError:
                self.message_var.set("Formato de mes invalido. Usa YYYY-MM.")
                return

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.calendar_text.configure(state="normal")
        self.calendar_text.delete("1.0", tk.END)
        self.calendar_text.configure(state="disabled")

        try:
            payload = self.app_state["api"].get_report("habitacions", params={"habitacio": room_value})
            rows = payload.get("data") or []
            filtered = [row for row in rows if isinstance(row, dict) and self._month_matches(row, month_value)]

            if not filtered:
                self.summary_var.set("")
                self.message_var.set("No hay ocupaciones para el filtro seleccionado.")
                self._render_calendar(month_value, [])
                return

            for row in filtered:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row.get("data_inici") or "-",
                        row.get("data_fi") or "-",
                        row.get("pacient") or "-",
                    ),
                )

            self.summary_var.set(f"Reservas: {len(filtered)}")
            self.message_var.set("Informe cargado correctamente.")
            self._render_calendar(month_value, filtered)
        except ApiError as exc:
            self.summary_var.set("")
            self.message_var.set(str(exc))
        except Exception as exc:
            self.summary_var.set("")
            self.message_var.set(f"Error: {exc}")

    def on_show(self):
        self.summary_var.set("")
        try:
            self._load_rooms()
            self.message_var.set("Selecciona habitacio y mes para consultar ocupacion.")
        except Exception as exc:
            self.message_var.set(f"No se pudieron cargar habitacions: {exc}")
