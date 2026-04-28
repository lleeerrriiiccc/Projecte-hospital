import datetime
import tkinter as tk
from tkinter import ttk

from ..api_client import ApiError
from .base import BaseView


class ReportVisitesView(BaseView):
    route = "report_visites"

    def __init__(self, master, app_state, navigate, *args, **kwargs):
        super().__init__(master, app_state, navigate, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        card = ttk.Frame(self, style="Card.TFrame", padding=20)
        card.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        card.columnconfigure(0, weight=1)
        card.rowconfigure(4, weight=1)

        ttk.Label(card, text="Informe de Visites", style="Title.TLabel").grid(row=0, column=0, sticky="w")

        controls = ttk.Frame(card)
        controls.grid(row=1, column=0, sticky="we", pady=(10, 8))

        ttk.Label(controls, text="Fecha (YYYY-MM-DD)").grid(row=0, column=0, sticky="w")
        self.date_entry = ttk.Entry(controls, width=16)
        self.date_entry.grid(row=0, column=1, sticky="w", padx=(8, 8))
        self.date_entry.insert(0, self.today_iso())

        ttk.Button(controls, text="Cargar", style="Primary.TButton", command=self._load_data).grid(row=0, column=2, sticky="w")
        ttk.Button(controls, text="Volver", command=lambda: self.navigate("home")).grid(row=0, column=3, sticky="w", padx=(8, 0))

        self.message_var = tk.StringVar(value="Selecciona una fecha para cargar visitas.")
        ttk.Label(card, textvariable=self.message_var, style="Muted.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 8))

        cols = ("hora", "pacient", "metge")
        self.tree = ttk.Treeview(card, columns=cols, show="headings", height=18)
        self.tree.heading("hora", text="Hora")
        self.tree.heading("pacient", text="Paciente")
        self.tree.heading("metge", text="Medico")
        self.tree.column("hora", width=120, anchor="center")
        self.tree.column("pacient", width=300, anchor="w")
        self.tree.column("metge", width=300, anchor="w")
        self.tree.grid(row=4, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=4, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def _load_data(self):
        date_value = self.date_entry.get().strip()
        try:
            self.parse_iso_date(date_value, "Formato de fecha invalido. Usa YYYY-MM-DD.")
        except ValueError as exc:
            self.message_var.set(str(exc))
            return

        self.clear_tree(self.tree)

        try:
            payload = self.app_state["api"].get_visites(date_value)
            rows = payload.get("data") or []

            if not rows:
                self.message_var.set("No hay visitas para esta fecha.")
                return

            for row in rows:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        row.get("hora_visita") or "-",
                        row.get("pacient") or "-",
                        row.get("metge") or "-",
                    ),
                )

            self.message_var.set("Informe cargado correctamente.")
        except ApiError as exc:
            self.message_var.set(str(exc))
        except Exception as exc:
            self.message_var.set(f"Error de conexion: {exc}")

    def on_show(self):
        self.message_var.set("Selecciona una fecha para cargar visitas.")
