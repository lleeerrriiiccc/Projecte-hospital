from __future__ import annotations

import datetime
import tkinter as tk
from tkinter import ttk

from ..api_client import ApiError
from .base import BaseView


class ReportQuirofansView(BaseView):
    route = "report_quirofans"

    def __init__(self, master, app_state, navigate, *args, **kwargs):
        super().__init__(master, app_state, navigate, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        card = ttk.Frame(self, style="Card.TFrame", padding=20)
        card.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        card.columnconfigure(0, weight=1)
        card.rowconfigure(3, weight=1)

        ttk.Label(card, text="Informe de Quirofans", style="Title.TLabel").grid(row=0, column=0, sticky="w")

        controls = ttk.Frame(card)
        controls.grid(row=1, column=0, sticky="we", pady=(10, 8))

        ttk.Label(controls, text="Fecha (YYYY-MM-DD)").grid(row=0, column=0, sticky="w")
        self.date_entry = ttk.Entry(controls, width=16)
        self.date_entry.grid(row=0, column=1, sticky="w", padx=(8, 8))
        self.date_entry.insert(0, datetime.date.today().isoformat())

        ttk.Button(controls, text="Cargar", style="Primary.TButton", command=self._load_data).grid(row=0, column=2, sticky="w")
        ttk.Button(controls, text="Volver", command=lambda: self.navigate("home")).grid(row=0, column=3, sticky="w", padx=(8, 0))

        self.message_var = tk.StringVar(value="Selecciona una fecha para cargar quirofans.")
        ttk.Label(card, textvariable=self.message_var, style="Muted.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 8))

        cols = ("id_operacio", "hora_operacio", "procediment", "pacient", "metge")
        self.tree = ttk.Treeview(card, columns=cols, show="headings", height=18)
        self.tree.heading("id_operacio", text="ID")
        self.tree.heading("hora_operacio", text="Hora")
        self.tree.heading("procediment", text="Procediment")
        self.tree.heading("pacient", text="Pacient")
        self.tree.heading("metge", text="Metge")
        self.tree.column("id_operacio", width=70, anchor="center")
        self.tree.column("hora_operacio", width=90, anchor="center")
        self.tree.column("procediment", width=240, anchor="w")
        self.tree.column("pacient", width=190, anchor="w")
        self.tree.column("metge", width=190, anchor="w")
        self.tree.grid(row=3, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=3, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def _load_data(self):
        date_value = self.date_entry.get().strip()
        try:
            datetime.datetime.strptime(date_value, "%Y-%m-%d")
        except ValueError:
            self.message_var.set("Formato de fecha invalido. Usa YYYY-MM-DD.")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            payload = self.app_state["api"].get_report("quirofans", params={"date": date_value})
            rows = payload.get("data") or []

            if not rows:
                self.message_var.set("No hay operaciones para esta fecha.")
                return

            for row in rows:
                if not isinstance(row, dict):
                    continue
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row.get("id_operacio") or "-",
                        row.get("hora_operacio") or "-",
                        row.get("procediment") or "-",
                        row.get("pacient") or "-",
                        row.get("metge") or "-",
                    ),
                )

            self.message_var.set("Informe cargado correctamente.")
        except ApiError as exc:
            self.message_var.set(str(exc))
        except Exception as exc:
            self.message_var.set(f"Error: {exc}")

    def on_show(self):
        self.message_var.set("Selecciona una fecha para cargar quirofans.")
