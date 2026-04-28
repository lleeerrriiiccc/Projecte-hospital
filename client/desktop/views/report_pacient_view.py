import tkinter as tk
from tkinter import ttk

from ..api_client import ApiError
from .base import BaseView


class ReportPacientView(BaseView):
    route = "report_pacient"

    def __init__(self, master, app_state, navigate, *args, **kwargs):
        super().__init__(master, app_state, navigate, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._patients_map = {}

        card = ttk.Frame(self, style="Card.TFrame", padding=20)
        card.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        card.columnconfigure(0, weight=1)
        card.rowconfigure(4, weight=1)

        ttk.Label(card, text="Informe de Pacient", style="Title.TLabel").grid(row=0, column=0, sticky="w")

        controls = ttk.Frame(card)
        controls.grid(row=1, column=0, sticky="we", pady=(10, 8))

        ttk.Label(controls, text="Pacient").grid(row=0, column=0, sticky="w")
        self.patient_combo = ttk.Combobox(controls, state="readonly", width=40)
        self.patient_combo.grid(row=0, column=1, sticky="w", padx=(8, 8))

        ttk.Button(controls, text="Cargar", style="Primary.TButton", command=self._load_data).grid(row=0, column=2, sticky="w")
        ttk.Button(controls, text="Volver", command=lambda: self.navigate("home")).grid(row=0, column=3, sticky="w", padx=(8, 0))

        self.message_var = tk.StringVar(value="Selecciona un pacient para ver su informe.")
        ttk.Label(card, textvariable=self.message_var, style="Muted.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 8))

        self.summary_var = tk.StringVar(value="")
        ttk.Label(card, textvariable=self.summary_var, style="Muted.TLabel").grid(row=3, column=0, sticky="w", pady=(0, 8))

        cols = ("tipus", "data_event", "hora_event", "descripcio", "info_extra")
        self.tree = ttk.Treeview(card, columns=cols, show="headings", height=16)
        self.tree.heading("tipus", text="Tipus")
        self.tree.heading("data_event", text="Data")
        self.tree.heading("hora_event", text="Hora")
        self.tree.heading("descripcio", text="Descripcio")
        self.tree.heading("info_extra", text="Info extra")
        self.tree.column("tipus", width=120, anchor="center")
        self.tree.column("data_event", width=110, anchor="center")
        self.tree.column("hora_event", width=90, anchor="center")
        self.tree.column("descripcio", width=260, anchor="w")
        self.tree.column("info_extra", width=230, anchor="w")
        self.tree.grid(row=4, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=4, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def _load_patients(self):
        payload = self.app_state["api"].get_pacients()
        rows = payload.get("data") or []
        self._patients_map = self.build_options_map(rows, ["id_pacient", "id"], ["nom_complet", "nom"])
        values = self.build_combo_values(self._patients_map)
        self.patient_combo.configure(values=values)
        if values and not self.patient_combo.get():
            self.patient_combo.set(values[0])

    def _load_data(self):
        patient_value = self.patient_combo.get().strip()
        if not patient_value:
            self.message_var.set("Selecciona un pacient.")
            return

        patient_id = self.split_combo_value(patient_value)

        self.clear_tree(self.tree)

        try:
            payload = self.app_state["api"].get_report("pacient", params={"pacient": patient_id})
            rows = payload.get("data") or []

            if not rows:
                self.summary_var.set("")
                self.message_var.set("No hay eventos para este pacient.")
                return

            by_type = {}
            for row in rows:
                if not isinstance(row, dict):
                    continue
                event_type = row.get("tipus") or "desconegut"
                by_type[event_type] = by_type.get(event_type, 0) + 1

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        event_type,
                        row.get("data_event") or "-",
                        row.get("hora_event") or "-",
                        row.get("descripcio") or "-",
                        row.get("info_extra") or "-",
                    ),
                )

            summary = ", ".join([f"{k}: {v}" for k, v in sorted(by_type.items())])
            self.summary_var.set(f"Totals -> {summary}")
            self.message_var.set("Informe cargado correctamente.")
        except ApiError as exc:
            self.summary_var.set("")
            self.message_var.set(str(exc))
        except Exception as exc:
            self.summary_var.set("")
            self.message_var.set(f"Error: {exc}")

    def on_show(self):
        self.summary_var.set("")
        try:
            self._load_patients()
            self.message_var.set("Selecciona un pacient para ver su informe.")
        except Exception as exc:
            self.message_var.set(f"No se pudieron cargar pacients: {exc}")
