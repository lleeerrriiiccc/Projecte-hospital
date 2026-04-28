import tkinter as tk
from tkinter import ttk

from ..api_client import ApiError
from .base import BaseView


class ReportSupervisioView(BaseView):
    route = "report_supervisio"

    def __init__(self, master, app_state, navigate, *args, **kwargs):
        super().__init__(master, app_state, navigate, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        card = ttk.Frame(self, style="Card.TFrame", padding=20)
        card.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        card.columnconfigure(0, weight=1)
        card.rowconfigure(3, weight=1)

        ttk.Label(card, text="Informe de Supervisio", style="Title.TLabel").grid(row=0, column=0, sticky="w")

        controls = ttk.Frame(card)
        controls.grid(row=1, column=0, sticky="we", pady=(10, 8))
        ttk.Button(controls, text="Cargar", style="Primary.TButton", command=self._load_data).grid(row=0, column=0, sticky="w")
        ttk.Button(controls, text="Volver", command=lambda: self.navigate("home")).grid(row=0, column=1, sticky="w", padx=(8, 0))

        self.message_var = tk.StringVar(value="Carga el informe de supervisio.")
        ttk.Label(card, textvariable=self.message_var, style="Muted.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 8))

        self.tree = ttk.Treeview(card, columns=("metge", "infermeres"), show="headings", height=18)
        self.tree.heading("metge", text="Metge supervisor")
        self.tree.heading("infermeres", text="Infermeres")
        self.tree.column("metge", width=260, anchor="w")
        self.tree.column("infermeres", width=600, anchor="w")
        self.tree.grid(row=3, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=3, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def _load_data(self):
        self.clear_tree(self.tree)

        try:
            payload = self.app_state["api"].get_report("supervisio")
            rows = payload.get("data") or []

            if not rows:
                self.message_var.set("No hay datos de supervisio.")
                return

            for row in rows:
                doctor = row[0] if isinstance(row, (list, tuple)) and len(row) > 0 else ""
                nurses = row[1] if isinstance(row, (list, tuple)) and len(row) > 1 else ""
                doctor_text = doctor or "Caps de planta (sense supervisor)"
                nurses_text = nurses or "-"
                self.tree.insert("", "end", values=(doctor_text, nurses_text))

            self.message_var.set("Informe cargado correctamente.")
        except ApiError as exc:
            self.message_var.set(str(exc))
        except Exception as exc:
            self.message_var.set(f"Error: {exc}")

    def on_show(self):
        self.message_var.set("Carga el informe de supervisio.")
