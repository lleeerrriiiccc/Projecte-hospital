import tkinter as tk
from tkinter import ttk

from ..api_client import ApiError
from .base import BaseView


class ReportAparellsView(BaseView):
    route = "report_aparells"

    def __init__(self, master, app_state, navigate, *args, **kwargs):
        super().__init__(master, app_state, navigate, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        card = ttk.Frame(self, style="Card.TFrame", padding=20)
        card.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        card.columnconfigure(0, weight=1)
        card.rowconfigure(4, weight=1)
        card.rowconfigure(6, weight=1)

        ttk.Label(card, text="Informe d'Aparells", style="Title.TLabel").grid(row=0, column=0, sticky="w")

        controls = ttk.Frame(card)
        controls.grid(row=1, column=0, sticky="we", pady=(10, 8))
        ttk.Button(controls, text="Cargar", style="Primary.TButton", command=self._load_data).grid(row=0, column=0, sticky="w")
        ttk.Button(controls, text="Volver", command=lambda: self.navigate("home")).grid(row=0, column=1, sticky="w", padx=(8, 0))

        self.message_var = tk.StringVar(value="Carga el informe de aparells.")
        ttk.Label(card, textvariable=self.message_var, style="Muted.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 8))

        summary = ttk.Frame(card)
        summary.grid(row=3, column=0, sticky="we", pady=(0, 8))
        summary.columnconfigure((0, 1), weight=1)

        self.rooms_var = tk.StringVar(value="Quirofans: 0")
        self.machines_var = tk.StringVar(value="Maquines totals: 0")

        ttk.Label(summary, textvariable=self.rooms_var, style="Muted.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(summary, textvariable=self.machines_var, style="Muted.TLabel").grid(row=0, column=1, sticky="w")

        self.cards_text = tk.Text(
            card,
            height=8,
            wrap="word",
            relief="solid",
            borderwidth=1,
            background="#ffffff",
        )
        self.cards_text.grid(row=4, column=0, sticky="nsew", pady=(0, 8))

        cards_scroll = ttk.Scrollbar(card, orient="vertical", command=self.cards_text.yview)
        cards_scroll.grid(row=4, column=1, sticky="ns", pady=(0, 8))
        self.cards_text.configure(yscrollcommand=cards_scroll.set)

        cols = ("id_quirofan", "planta", "maquinari")
        self.tree = ttk.Treeview(card, columns=cols, show="headings", height=18)
        self.tree.heading("id_quirofan", text="Quirofan")
        self.tree.heading("planta", text="Planta")
        self.tree.heading("maquinari", text="Maquinari")
        self.tree.column("id_quirofan", width=110, anchor="center")
        self.tree.column("planta", width=110, anchor="center")
        self.tree.column("maquinari", width=620, anchor="w")
        self.tree.grid(row=6, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=6, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def _parse_machines(self, machine_text):
        raw = str(machine_text or "")
        return [item.strip() for item in raw.split(",") if item.strip()]

    def _render_cards(self, rows):
        self.cards_text.configure(state="normal")
        self.cards_text.delete("1.0", tk.END)

        total_machines = 0
        for row in rows:
            if not isinstance(row, dict):
                continue
            machines = self._parse_machines(row.get("maquinari"))
            total_machines += len(machines)

            room = row.get("id_quirofan") or "-"
            floor = row.get("planta") or "-"
            machines_text = ", ".join(machines) if machines else "Sense aparells"
            count_text = len(machines)

            self.cards_text.insert(
                tk.END,
                f"Quirofan {room} · Planta {floor}\n{count_text} maquines: {machines_text}\n\n",
            )

        self.rooms_var.set(f"Quirofans: {len(rows)}")
        self.machines_var.set(f"Maquines totals: {total_machines}")
        self.cards_text.configure(state="disabled")

    def _load_data(self):
        self.clear_tree(self.tree)
        self.clear_text_widget(self.cards_text)
        self.cards_text.configure(state="disabled")
        self.rooms_var.set("Quirofans: 0")
        self.machines_var.set("Maquines totals: 0")

        try:
            payload = self.app_state["api"].get_report("aparells")
            rows = payload.get("data") or []
            if not rows:
                self.message_var.set("No hay datos de aparells.")
                return

            self._render_cards(rows)

            for row in rows:
                if isinstance(row, dict):
                    values = (
                        row.get("id_quirofan") or "-",
                        row.get("planta") or "-",
                        row.get("maquinari") or "-",
                    )
                else:
                    values = ("-", "-", str(row))
                self.tree.insert("", "end", values=values)

            self.message_var.set("Informe cargado correctamente.")
        except ApiError as exc:
            self.message_var.set(str(exc))
        except Exception as exc:
            self.message_var.set(f"Error: {exc}")

    def on_show(self):
        self.message_var.set("Carga el informe de aparells.")
