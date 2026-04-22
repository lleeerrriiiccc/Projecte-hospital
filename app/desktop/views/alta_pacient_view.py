from __future__ import annotations

import datetime
import tkinter as tk
from tkinter import ttk

from ..api_client import ApiError
from .base import BaseView


class AltaPacientView(BaseView):
    route = "alta_pacient"

    def __init__(self, master, app_state, navigate, *args, **kwargs):
        super().__init__(master, app_state, navigate, *args, **kwargs)

        self.columnconfigure(0, weight=1)

        card = ttk.Frame(self, style="Card.TFrame", padding=20)
        card.grid(row=0, column=0, sticky="n", padx=16, pady=16)
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="Alta de Paciente", style="Title.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(card, text="Introduce los datos del paciente.", style="Muted.TLabel").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(5, 10)
        )

        self.status_var = tk.StringVar(value="")
        self.status_lbl = ttk.Label(card, textvariable=self.status_var, style="Muted.TLabel")
        self.status_lbl.grid(row=2, column=0, columnspan=2, sticky="we", pady=(0, 8))

        self.fields = {}
        labels = [
            ("Nom", "nom"),
            ("Primer cognom", "cognom"),
            ("Segon cognom", "cognom2"),
            ("Data naixement (YYYY-MM-DD)", "data_naixement"),
            ("Identificador", "identificador"),
        ]

        for idx, (label, key) in enumerate(labels, start=3):
            ttk.Label(card, text=label).grid(row=idx, column=0, sticky="w", pady=3)
            entry = ttk.Entry(card, width=36)
            entry.grid(row=idx, column=1, sticky="we", pady=3)
            self.fields[key] = entry

        self.fields["data_naixement"].insert(0, "1990-01-01")

        buttons = ttk.Frame(card)
        buttons.grid(row=9, column=0, columnspan=2, sticky="we", pady=(10, 0))
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)

        ttk.Button(buttons, text="Guardar", style="Primary.TButton", command=self._submit).grid(row=0, column=0, sticky="we", padx=(0, 6))
        ttk.Button(buttons, text="Volver", command=lambda: self.navigate("home")).grid(row=0, column=1, sticky="we", padx=(6, 0))

    def _show_status(self, text):
        self.status_var.set(text)

    def _validate(self, payload):
        for key, value in payload.items():
            if not value:
                raise ValueError("Completa todos los campos.")

        try:
            parsed_date = datetime.datetime.strptime(payload["data_naixement"], "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("La fecha debe tener formato YYYY-MM-DD.") from exc

        if parsed_date > datetime.date.today():
            raise ValueError("La fecha de nacimiento no puede ser futura.")

    def _submit(self):
        payload = {key: entry.get().strip() for key, entry in self.fields.items()}
        payload["identificador"] = payload["identificador"].upper()

        try:
            self._validate(payload)
            self.app_state["api"].create_patient(**payload)
            self._show_status("Paciente dado de alta correctamente.")
            for entry in self.fields.values():
                entry.delete(0, tk.END)
            self.fields["data_naixement"].insert(0, "1990-01-01")
        except (ApiError, ValueError) as exc:
            self._show_status(str(exc))
        except Exception as exc:
            self._show_status(f"Error inesperado: {exc}")

    def on_show(self):
        self._show_status("")
