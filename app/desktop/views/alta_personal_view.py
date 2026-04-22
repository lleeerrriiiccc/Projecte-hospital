from __future__ import annotations

import datetime
import tkinter as tk
from tkinter import filedialog, ttk

from ..api_client import ApiError
from .base import BaseView


WORK_TYPES = [
    "metge",
    "infermer",
    "administratiu",
    "tecnic",
    "personal neteja",
    "personal seguretat",
    "personal cuina",
]


class AltaPersonalView(BaseView):
    route = "alta_personal"

    def __init__(self, master, app_state, navigate, *args, **kwargs):
        super().__init__(master, app_state, navigate, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        card = ttk.Frame(self, style="Card.TFrame", padding=20)
        card.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="Alta de Personal", style="Title.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(card, text="Introduce los datos obligatorios del personal.", style="Muted.TLabel").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(5, 8)
        )

        self.status_var = tk.StringVar(value="")
        ttk.Label(card, textvariable=self.status_var, style="Muted.TLabel").grid(row=2, column=0, columnspan=2, sticky="we")

        self.entries = {}
        self._build_main_fields(card)

        self.dynamic_frame = ttk.Frame(card)
        self.dynamic_frame.grid(row=14, column=0, columnspan=2, sticky="we", pady=(4, 0))
        self.dynamic_frame.columnconfigure(1, weight=1)

        buttons = ttk.Frame(card)
        buttons.grid(row=15, column=0, columnspan=2, sticky="we", pady=(12, 0))
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)

        ttk.Button(buttons, text="Guardar", style="Primary.TButton", command=self._submit).grid(
            row=0, column=0, sticky="we", padx=(0, 6)
        )
        ttk.Button(buttons, text="Volver", command=lambda: self.navigate("home")).grid(
            row=0, column=1, sticky="we", padx=(6, 0)
        )

        self._metges_map = {}
        self.cap_de_planta_var = tk.BooleanVar(value=False)
        self.cv_path_var = tk.StringVar(value="")
        self._render_dynamic_fields()

    def _build_main_fields(self, card):
        fields = [
            ("Nom", "nom"),
            ("Primer cognom", "cognom"),
            ("Segon cognom", "cognom2"),
            ("Data naixement (YYYY-MM-DD)", "data_naixement"),
            ("Telefon principal", "telefon"),
            ("Telefon secundari", "telefon2"),
            ("Email personal", "email"),
            ("Email intern", "email_intern"),
            ("DNI", "dni"),
            ("Data alta (YYYY-MM-DD)", "data_alta"),
        ]

        row = 3
        for label, key in fields:
            ttk.Label(card, text=label).grid(row=row, column=0, sticky="w", pady=3)
            entry = ttk.Entry(card, width=42)
            entry.grid(row=row, column=1, sticky="we", pady=3)
            self.entries[key] = entry
            row += 1

        self.entries["data_alta"].insert(0, datetime.date.today().isoformat())

        ttk.Label(card, text="Tipus feina").grid(row=13, column=0, sticky="w", pady=3)
        self.tipus_combo = ttk.Combobox(card, values=WORK_TYPES, state="readonly")
        self.tipus_combo.grid(row=13, column=1, sticky="we", pady=3)
        self.tipus_combo.bind("<<ComboboxSelected>>", lambda _evt: self._render_dynamic_fields())

    def _clear_dynamic(self):
        for child in self.dynamic_frame.winfo_children():
            child.destroy()

    def _load_metges(self):
        if self._metges_map:
            return

        payload = self.app_state["api"].get_metges()
        rows = payload.get("data") or []
        metges = {}
        for row in rows:
            if isinstance(row, (list, tuple)) and len(row) >= 2:
                metges[str(row[0])] = str(row[1])
            elif isinstance(row, dict):
                metge_id = row.get("id_intern") or row.get("id")
                metge_name = row.get("nom_complet") or row.get("nom")
                if metge_id and metge_name:
                    metges[str(metge_id)] = str(metge_name)
        self._metges_map = metges

    def _browse_cv(self):
        file_path = filedialog.askopenfilename(
            title="Selecciona el CV",
            filetypes=[("Documents", "*.pdf *.doc *.docx"), ("All files", "*.*")],
        )
        if file_path:
            self.cv_path_var.set(file_path)

    def _toggle_supervisor(self):
        if not hasattr(self, "supervisor_combo"):
            return

        if self.cap_de_planta_var.get():
            self.supervisor_combo.configure(state="disabled")
            self.supervisor_combo.set("")
        else:
            self.supervisor_combo.configure(state="readonly")

    def _render_dynamic_fields(self):
        self._clear_dynamic()
        selected = self.tipus_combo.get().strip()

        if selected == "metge":
            ttk.Label(self.dynamic_frame, text="Especialitat").grid(row=0, column=0, sticky="w", pady=3)
            self.especialitat_entry = ttk.Entry(self.dynamic_frame)
            self.especialitat_entry.grid(row=0, column=1, sticky="we", pady=3)

            ttk.Label(self.dynamic_frame, text="CV").grid(row=1, column=0, sticky="w", pady=3)
            cv_frame = ttk.Frame(self.dynamic_frame)
            cv_frame.grid(row=1, column=1, sticky="we", pady=3)
            cv_frame.columnconfigure(0, weight=1)
            ttk.Entry(cv_frame, textvariable=self.cv_path_var).grid(row=0, column=0, sticky="we")
            ttk.Button(cv_frame, text="Seleccionar", command=self._browse_cv).grid(row=0, column=1, padx=(6, 0))
            return

        if selected == "infermer":
            try:
                self._load_metges()
            except Exception as exc:
                self.status_var.set(f"No se pudieron cargar metges: {exc}")
                return

            ttk.Checkbutton(
                self.dynamic_frame,
                text="Cap de planta",
                variable=self.cap_de_planta_var,
                command=self._toggle_supervisor,
            ).grid(row=0, column=0, columnspan=2, sticky="w", pady=3)

            ttk.Label(self.dynamic_frame, text="Metge supervisor").grid(row=1, column=0, sticky="w", pady=3)
            values = [f"{mid} - {name}" for mid, name in self._metges_map.items()]
            self.supervisor_combo = ttk.Combobox(self.dynamic_frame, values=values, state="readonly")
            self.supervisor_combo.grid(row=1, column=1, sticky="we", pady=3)
            self._toggle_supervisor()

    def _validate_dates(self, payload):
        try:
            birth_date = datetime.datetime.strptime(payload["data_naixement"], "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("Data naixement invalida. Usa YYYY-MM-DD.") from exc

        if birth_date > datetime.date.today():
            raise ValueError("La data de naixement no pot ser futura.")

        try:
            datetime.datetime.strptime(payload["data_alta"], "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("Data alta invalida. Usa YYYY-MM-DD.") from exc

    def _build_payload(self):
        payload = {key: entry.get().strip() for key, entry in self.entries.items()}
        payload["tipus_feina"] = self.tipus_combo.get().strip()
        payload["dni"] = payload["dni"].upper()

        required = [
            "nom",
            "cognom",
            "cognom2",
            "data_naixement",
            "telefon",
            "email",
            "email_intern",
            "dni",
            "tipus_feina",
            "data_alta",
        ]
        missing = [key for key in required if not payload.get(key)]
        if missing:
            raise ValueError("Completa todos los campos obligatorios.")

        self._validate_dates(payload)

        if payload["tipus_feina"] == "metge":
            especialitat = getattr(self, "especialitat_entry", None)
            if not especialitat or not especialitat.get().strip():
                raise ValueError("Especialitat es obligatoria para metge.")
            if not self.cv_path_var.get().strip():
                raise ValueError("CV es obligatorio para metge.")
            payload["especialitat"] = especialitat.get().strip()
            payload["cv_path"] = self.cv_path_var.get().strip()

        if payload["tipus_feina"] == "infermer":
            payload["cap_de_planta"] = bool(self.cap_de_planta_var.get())
            if not payload["cap_de_planta"]:
                selected = getattr(self, "supervisor_combo", None)
                selected_value = selected.get().strip() if selected else ""
                if not selected_value:
                    raise ValueError("Selecciona un metge supervisor o marca cap de planta.")
                payload["id_metge_supervisor"] = selected_value.split(" - ", 1)[0]

        return payload

    def _submit(self):
        try:
            payload = self._build_payload()
            self.app_state["api"].create_personal(payload)
            self.status_var.set("Personal dado de alta correctamente.")
            self._reset_form()
        except (ApiError, ValueError) as exc:
            self.status_var.set(str(exc))
        except Exception as exc:
            self.status_var.set(f"Error inesperado: {exc}")

    def _reset_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.entries["data_alta"].insert(0, datetime.date.today().isoformat())
        self.tipus_combo.set("")
        self.cv_path_var.set("")
        self.cap_de_planta_var.set(False)
        self._render_dynamic_fields()

    def on_show(self):
        self.status_var.set("")
