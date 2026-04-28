import os
import sys
import tkinter as tk
from tkinter import ttk

try:
    from .api_client import ApiClient
    from .config import WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH
    from .theme import PALETTE
    from .views.alta_pacient_view import AltaPacientView
    from .views.alta_personal_view import AltaPersonalView
    from .views.report_aparells_view import ReportAparellsView
    from .views.report_habitacions_view import ReportHabitacionsView
    from .views.report_metge_view import ReportMetgeView
    from .views.report_pacient_view import ReportPacientView
    from .views.report_quirofans_view import ReportQuirofansView
    from .views.report_supervisio_view import ReportSupervisioView
    from .views.home_view import HomeView
    from .views.login_view import LoginView
    from .views.report_visites_view import ReportVisitesView
except ImportError:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    client_dir = os.path.dirname(current_dir)

    if client_dir not in sys.path:
        sys.path.insert(0, client_dir)

    from desktop.api_client import ApiClient
    from desktop.config import WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH
    from desktop.theme import PALETTE
    from desktop.views.alta_pacient_view import AltaPacientView
    from desktop.views.alta_personal_view import AltaPersonalView
    from desktop.views.report_aparells_view import ReportAparellsView
    from desktop.views.report_habitacions_view import ReportHabitacionsView
    from desktop.views.report_metge_view import ReportMetgeView
    from desktop.views.report_pacient_view import ReportPacientView
    from desktop.views.report_quirofans_view import ReportQuirofansView
    from desktop.views.report_supervisio_view import ReportSupervisioView
    from desktop.views.home_view import HomeView
    from desktop.views.login_view import LoginView
    from desktop.views.report_visites_view import ReportVisitesView


class DesktopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Projecte Hospital - Desktop")
        self.configure(bg=PALETTE["bg"])
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.geometry("1320x840")

        self._setup_styles()

        self.app_state = {
            "api": ApiClient(),
            "username": None,
            "role": None,
        }

        self.container = ttk.Frame(self, style="App.TFrame")
        self.container.pack(fill="both", expand=True)
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=1)

        self.views = {}
        self._register_views()

        self.show_view("login")

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        self.option_add("*Font", "Bahnschrift 10")

        # Base surfaces and layout containers.
        style.configure("App.TFrame", background=PALETTE["bg"])
        style.configure("Topbar.TFrame", background=PALETTE["primary"], relief="flat")
        style.configure("Card.TFrame", background=PALETTE["surface"], relief="flat")

        # Typography hierarchy.
        style.configure("TLabel", background=PALETTE["surface"], foreground=PALETTE["text"], font=("Bahnschrift", 10))
        style.configure("Title.TLabel", background=PALETTE["surface"], foreground=PALETTE["primary"], font=("Bahnschrift", 19, "bold"))
        style.configure("TopbarTitle.TLabel", background=PALETTE["primary"], foreground=PALETTE["topbar_text"], font=("Bahnschrift", 16, "bold"))
        style.configure("TopbarMuted.TLabel", background=PALETTE["primary"], foreground=PALETTE["topbar_text"], font=("Bahnschrift", 10))
        style.configure("Muted.TLabel", background=PALETTE["surface"], foreground=PALETTE["muted"], font=("Bahnschrift", 10))
        style.configure("Section.TLabel", background=PALETTE["surface"], foreground=PALETTE["primary_dark"], font=("Bahnschrift", 11, "bold"))
        style.configure("Error.TLabel", background=PALETTE["error_bg"], foreground=PALETTE["error_text"], padding=(10, 8), font=("Bahnschrift", 10, "bold"))

        # Inputs and selection widgets.
        style.configure(
            "TEntry",
            fieldbackground="white",
            bordercolor=PALETTE["border"],
            foreground=PALETTE["text"],
            insertcolor=PALETTE["text"],
            padding=(8, 6),
        )
        style.map("TEntry", bordercolor=[("focus", PALETTE["focus"])])
        style.configure("TCombobox", padding=(6, 5), fieldbackground="white", foreground=PALETTE["text"])

        # Primary and secondary actions.
        style.configure("TButton", font=("Bahnschrift", 10, "bold"), padding=(12, 9), borderwidth=0)
        style.configure("Primary.TButton", foreground="white", background=PALETTE["primary"], borderwidth=0)
        style.map(
            "Primary.TButton",
            background=[("active", PALETTE["primary_dark"]), ("pressed", PALETTE["primary_dark"])],
        )
        style.configure("Secondary.TButton", foreground=PALETTE["text"], background=PALETTE["secondary_bg"], borderwidth=0)
        style.map(
            "Secondary.TButton",
            background=[("active", PALETTE["secondary_active"]), ("pressed", PALETTE["secondary_active"])],
        )

        # Data table readability and focus states.
        style.configure(
            "Treeview",
            rowheight=32,
            font=("Bahnschrift", 10),
            fieldbackground="white",
            background="white",
            foreground=PALETTE["text"],
            bordercolor=PALETTE["border"],
        )
        style.map("Treeview", background=[("selected", "#dcecf4")], foreground=[("selected", PALETTE["text"])])
        style.configure("Treeview.Heading", font=("Bahnschrift", 10, "bold"), background=PALETTE["primary"], foreground="white")

    def _register_views(self):
        view_classes = [
            LoginView,
            HomeView,
            AltaPacientView,
            AltaPersonalView,
            ReportVisitesView,
            ReportQuirofansView,
            ReportAparellsView,
            ReportSupervisioView,
            ReportHabitacionsView,
            ReportMetgeView,
            ReportPacientView,
        ]

        for cls in view_classes:
            view = cls(self.container, self.app_state, self.show_view, style="App.TFrame")
            view.grid(row=0, column=0, sticky="nsew")
            self.views[cls.route] = view

    def show_view(self, route):
        if route not in self.views:
            return

        if route != "login" and not self.app_state.get("username"):
            route = "login"

        view = self.views[route]
        view.tkraise()
        view.on_show()


def main():
    app = DesktopApp()
    app.mainloop()


if __name__ == "__main__":
    main()
