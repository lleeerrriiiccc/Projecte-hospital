import datetime
import tkinter as tk
from tkinter import ttk

from ..api_client import ApiError
from .base import BaseView


class ReportMetgeView(BaseView):
    route = "report_metge"

    def __init__(self, master, app_state, navigate, *args, **kwargs):
        super().__init__(master, app_state, navigate, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._metges_map = {}

        card = ttk.Frame(self, style="Card.TFrame", padding=20)
        card.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        card.columnconfigure(0, weight=1)
        card.rowconfigure(4, weight=1)
        card.rowconfigure(6, weight=1)

        ttk.Label(card, text="Informe Horari de Metge", style="Title.TLabel").grid(row=0, column=0, sticky="w")

        controls = ttk.Frame(card)
        controls.grid(row=1, column=0, sticky="we", pady=(10, 8))

        ttk.Label(controls, text="Metge").grid(row=0, column=0, sticky="w")
        self.doctor_combo = ttk.Combobox(controls, state="readonly", width=32)
        self.doctor_combo.grid(row=0, column=1, sticky="w", padx=(8, 14))

        ttk.Label(controls, text="Fecha (YYYY-MM-DD)").grid(row=0, column=2, sticky="w")
        self.date_entry = ttk.Entry(controls, width=16)
        self.date_entry.grid(row=0, column=3, sticky="w", padx=(8, 8))
        self.date_entry.insert(0, self.today_iso())

        ttk.Button(controls, text="Cargar", style="Primary.TButton", command=self._load_data).grid(row=0, column=4, sticky="w")
        ttk.Button(controls, text="Volver", command=lambda: self.navigate("home")).grid(row=0, column=5, sticky="w", padx=(8, 0))

        self.message_var = tk.StringVar(value="Selecciona metge y fecha para consultar.")
        ttk.Label(card, textvariable=self.message_var, style="Muted.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 8))

        summary = ttk.Frame(card)
        summary.grid(row=3, column=0, sticky="we", pady=(0, 8))
        summary.columnconfigure((0, 1, 2), weight=1)

        self.occupied_var = tk.StringVar(value="Franges ocupades: 0")
        self.free_var = tk.StringVar(value="Franges lliures: 25")
        self.events_var = tk.StringVar(value="Actes del dia: 0")

        ttk.Label(summary, textvariable=self.occupied_var, style="Muted.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(summary, textvariable=self.free_var, style="Muted.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Label(summary, textvariable=self.events_var, style="Muted.TLabel").grid(row=0, column=2, sticky="w")

        timeline_frame = ttk.Frame(card)
        timeline_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 8))
        timeline_frame.columnconfigure(0, weight=1)
        timeline_frame.rowconfigure(1, weight=1)

        ttk.Label(timeline_frame, text="Calendari diari", style="Muted.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 4))

        tl_cols = ("hora", "estat", "detall")
        self.timeline_tree = ttk.Treeview(timeline_frame, columns=tl_cols, show="headings", height=9)
        self.timeline_tree.heading("hora", text="Hora")
        self.timeline_tree.heading("estat", text="Estat")
        self.timeline_tree.heading("detall", text="Detall")
        self.timeline_tree.column("hora", width=90, anchor="center")
        self.timeline_tree.column("estat", width=110, anchor="center")
        self.timeline_tree.column("detall", width=580, anchor="w")
        self.timeline_tree.grid(row=1, column=0, sticky="nsew")

        tl_scrollbar = ttk.Scrollbar(timeline_frame, orient="vertical", command=self.timeline_tree.yview)
        tl_scrollbar.grid(row=1, column=1, sticky="ns")
        self.timeline_tree.configure(yscrollcommand=tl_scrollbar.set)

        cols = ("hora", "tipus", "pacient", "detall")
        self.tree = ttk.Treeview(card, columns=cols, show="headings", height=17)
        self.tree.heading("hora", text="Hora")
        self.tree.heading("tipus", text="Tipus")
        self.tree.heading("pacient", text="Pacient")
        self.tree.heading("detall", text="Detall")
        self.tree.column("hora", width=100, anchor="center")
        self.tree.column("tipus", width=90, anchor="center")
        self.tree.column("pacient", width=210, anchor="w")
        self.tree.column("detall", width=380, anchor="w")
        self.tree.grid(row=6, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=6, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def _normalize_hour(self, value):
        text = str(value or "")
        if not text:
            return ""
        parts = text.split(":")
        if len(parts) < 2:
            return ""
        try:
            return f"{int(parts[0]):02d}:00"
        except ValueError:
            return ""

    def _render_timeline(self, rows):
        for item in self.timeline_tree.get_children():
            self.timeline_tree.delete(item)

        grouped = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            hour_key = self._normalize_hour(row.get("hora"))
            if not hour_key:
                continue
            grouped.setdefault(hour_key, []).append(row)

        occupied = len(grouped.keys())
        total_slots = 25
        free = total_slots - occupied

        self.occupied_var.set(f"Franges ocupades: {occupied}")
        self.free_var.set(f"Franges lliures: {free}")
        self.events_var.set(f"Actes del dia: {len(rows)}")

        for hour in range(25):
            hour_key = f"{hour:02d}:00"
            events = grouped.get(hour_key, [])
            if events:
                details = []
                for event in events:
                    event_type = str(event.get("tipus") or "acte")
                    patient = str(event.get("pacient") or "-")
                    detail = str(event.get("detall") or "-")
                    details.append(f"{event_type}: {patient} ({detail})")
                detail_text = " | ".join(details)
                self.timeline_tree.insert("", "end", values=(hour_key, "Ocupat", detail_text))
            else:
                self.timeline_tree.insert("", "end", values=(hour_key, "Lliure", "Sense actes"))

    def _load_metges(self):
        payload = self.app_state["api"].get_metges()
        rows = payload.get("data") or []
        self._metges_map = self.build_options_map(rows, ["id_intern", "id"], ["nom_complet", "nom"])
        values = self.build_combo_values(self._metges_map)
        self.doctor_combo.configure(values=values)
        if values and not self.doctor_combo.get():
            self.doctor_combo.set(values[0])

    def _load_data(self):
        doctor_value = self.doctor_combo.get().strip()
        date_value = self.date_entry.get().strip()

        if not doctor_value:
            self.message_var.set("Selecciona un metge.")
            return

        try:
            self.parse_iso_date(date_value, "Formato de fecha invalido. Usa YYYY-MM-DD.")
        except ValueError as exc:
            self.message_var.set(str(exc))
            return

        doctor_id = self.split_combo_value(doctor_value)

        self.clear_tree(self.tree)
        self.clear_tree(self.timeline_tree)

        self.occupied_var.set("Franges ocupades: 0")
        self.free_var.set("Franges lliures: 25")
        self.events_var.set("Actes del dia: 0")

        try:
            payload = self.app_state["api"].get_report("metge", params={"metge": doctor_id, "date": date_value})
            rows = payload.get("data") or []

            if not rows:
                self.message_var.set("No hay agenda para este metge y fecha.")
                self._render_timeline([])
                return

            for row in rows:
                if not isinstance(row, dict):
                    continue
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row.get("hora") or "-",
                        row.get("tipus") or "-",
                        row.get("pacient") or "-",
                        row.get("detall") or "-",
                    ),
                )

            self.message_var.set("Informe cargado correctamente.")
            self._render_timeline(rows)
        except ApiError as exc:
            self.message_var.set(str(exc))
        except Exception as exc:
            self.message_var.set(f"Error: {exc}")

    def on_show(self):
        try:
            self._load_metges()
            self.message_var.set("Selecciona metge y fecha para consultar.")
        except Exception as exc:
            self.message_var.set(f"No se pudieron cargar metges: {exc}")
