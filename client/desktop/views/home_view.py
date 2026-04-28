import tkinter as tk
from tkinter import ttk

from ..api_client import ApiError
from .base import BaseView


class HomeView(BaseView):
    route = "home"

    def __init__(self, master, app_state, navigate, *args, **kwargs):
        super().__init__(master, app_state, navigate, *args, **kwargs)

        # Global layout: top bar + content area.
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        topbar = ttk.Frame(self, style="Topbar.TFrame", padding=(18, 12))
        topbar.grid(row=0, column=0, sticky="we")
        topbar.columnconfigure(0, weight=1)

        ttk.Label(topbar, text="Gestio Hospitalaria", style="TopbarTitle.TLabel").grid(row=0, column=0, sticky="w")

        self.user_label = ttk.Label(topbar, text="", style="TopbarMuted.TLabel")
        self.user_label.grid(row=0, column=1, sticky="e")

        main = ttk.Frame(self, padding=16)
        main.grid(row=1, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)

        card = ttk.Frame(main, style="Card.TFrame", padding=18)
        card.grid(row=0, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)

        ttk.Label(card, text="Panell principal", style="Title.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        # Navigation grouped by hospital domain.
        sections = [
            (
                "Pacients",
                [
                    ("Nou pacient", lambda: self.navigate("alta_pacient")),
                    ("Informe pacient", lambda: self.navigate("report_pacient")),
                ],
            ),
            (
                "Enfermeria",
                [
                    ("Informe supervisio", lambda: self.navigate("report_supervisio")),
                ],
            ),
            (
                "Personal",
                [
                    ("Nou personal", lambda: self.navigate("alta_personal")),
                ],
            ),
            (
                "Visites",
                [
                    ("Veure visites", lambda: self.navigate("report_visites")),
                    ("Horari metge", lambda: self.navigate("report_metge")),
                ],
            ),
            (
                "Quirofans",
                [
                    ("Veure quirofans", lambda: self.navigate("report_quirofans")),
                    ("Aparells", lambda: self.navigate("report_aparells")),
                ],
            ),
            (
                "Habitacions",
                [
                    ("Veure ocupacio", lambda: self.navigate("report_habitacions")),
                ],
            ),
        ]

        row = 1
        for section_title, section_actions in sections:
            ttk.Label(card, text=section_title, style="Section.TLabel").grid(row=row, column=0, sticky="w", pady=(12, 4))
            row += 1
            for label, command in section_actions:
                ttk.Button(card, text=label, command=command, style="Primary.TButton").grid(
                    row=row,
                    column=0,
                    sticky="we",
                    pady=4,
                )
                row += 1

        ttk.Separator(card, orient="horizontal").grid(row=row, column=0, sticky="we", pady=(12, 8))
        row += 1
        ttk.Button(card, text="Tancar sessio", command=self._logout, style="Secondary.TButton").grid(row=row, column=0, sticky="we")

    def _logout(self):
        # Local logout resets session state even if the API call fails.
        try:
            self.app_state["api"].logout()
        except ApiError:
            pass
        self.app_state["username"] = None
        self.app_state["role"] = None
        self.navigate("login")

    def on_show(self):
        username = self.app_state.get("username") or "-"
        self.user_label.configure(text=f"Hola, {username}")
