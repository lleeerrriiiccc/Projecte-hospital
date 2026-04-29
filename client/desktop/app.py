import tkinter as tk
from tkinter import ttk

from . import api_client as api
from .config import WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH
from .theme import PALETTE
from .views.alta_pacient_view import create_alta_pacient_view
from .views.alta_personal_view import create_alta_personal_view
from .views.report_aparells_view import create_report_aparells_view
from .views.report_habitacions_view import create_report_habitacions_view
from .views.report_metge_view import create_report_metge_view
from .views.report_pacient_view import create_report_pacient_view
from .views.report_quirofans_view import create_report_quirofans_view
from .views.report_supervisio_view import create_report_supervisio_view
from .views.home_view import create_home_view
from .views.login_view import create_login_view
from .views.report_visites_view import create_report_visites_view


def setup_styles(root):
    style = ttk.Style(root)
    style.theme_use('clam')
    root.option_add('*Font', 'Bahnschrift 10')

    style.configure('App.TFrame', background=PALETTE['bg'])
    style.configure('Topbar.TFrame', background=PALETTE['primary'], relief='flat')
    style.configure('Card.TFrame', background=PALETTE['surface'], relief='flat')

    style.configure('TLabel', background=PALETTE['surface'], foreground=PALETTE['text'], font=('Bahnschrift', 10))
    style.configure('Title.TLabel', background=PALETTE['surface'], foreground=PALETTE['primary'], font=('Bahnschrift', 19, 'bold'))
    style.configure('TopbarTitle.TLabel', background=PALETTE['primary'], foreground=PALETTE['topbar_text'], font=('Bahnschrift', 16, 'bold'))
    style.configure('TopbarMuted.TLabel', background=PALETTE['primary'], foreground=PALETTE['topbar_text'], font=('Bahnschrift', 10))
    style.configure('Muted.TLabel', background=PALETTE['surface'], foreground=PALETTE['muted'], font=('Bahnschrift', 10))
    style.configure('Section.TLabel', background=PALETTE['surface'], foreground=PALETTE['primary_dark'], font=('Bahnschrift', 11, 'bold'))
    style.configure('Error.TLabel', background=PALETTE['error_bg'], foreground=PALETTE['error_text'], padding=(10, 8), font=('Bahnschrift', 10, 'bold'))

    style.configure('TEntry', fieldbackground='white', bordercolor=PALETTE['border'], foreground=PALETTE['text'], insertcolor=PALETTE['text'], padding=(8, 6))
    style.map('TEntry', bordercolor=[('focus', PALETTE['focus'])])
    style.configure('TCombobox', padding=(6, 5), fieldbackground='white', foreground=PALETTE['text'])

    style.configure('TButton', font=('Bahnschrift', 10, 'bold'), padding=(12, 9), borderwidth=0)
    style.configure('Primary.TButton', foreground='white', background=PALETTE['primary'], borderwidth=0)
    style.map('Primary.TButton', background=[('active', PALETTE['primary_dark']), ('pressed', PALETTE['primary_dark'])])
    style.configure('Secondary.TButton', foreground=PALETTE['text'], background=PALETTE['secondary_bg'], borderwidth=0)
    style.map('Secondary.TButton', background=[('active', PALETTE['secondary_active']), ('pressed', PALETTE['secondary_active'])])

    style.configure('Treeview', rowheight=32, font=('Bahnschrift', 10), fieldbackground='white', background='white', foreground=PALETTE['text'], bordercolor=PALETTE['border'])
    style.map('Treeview', background=[('selected', '#dcecf4')], foreground=[('selected', PALETTE['text'])])
    style.configure('Treeview.Heading', font=('Bahnschrift', 10, 'bold'), background=PALETTE['primary'], foreground='white')


def main():
    root = tk.Tk()
    root.title('Projecte Hospital - Desktop')
    root.configure(bg=PALETTE['bg'])
    root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
    root.geometry('1320x840')

    setup_styles(root)

    # Estat compartit entre totes les vistes
    app_state = {
        'username': None,
        'role': None,
    }

    container = ttk.Frame(root, style='App.TFrame')
    container.pack(fill='both', expand=True)
    container.columnconfigure(0, weight=1)
    container.rowconfigure(0, weight=1)

    views = {}
    on_show_callbacks = {}

    def navigate(route):
        if route not in views:
            return
        # Si no ha iniciat sessió, redirigir al login
        if route != 'login' and not app_state.get('username'):
            route = 'login'
        views[route].tkraise()
        if route in on_show_callbacks:
            on_show_callbacks[route]()

    # Llista de totes les vistes: (nom_ruta, funció_creadora)
    all_views = [
        ('login', create_login_view),
        ('home', create_home_view),
        ('alta_pacient', create_alta_pacient_view),
        ('alta_personal', create_alta_personal_view),
        ('report_visites', create_report_visites_view),
        ('report_quirofans', create_report_quirofans_view),
        ('report_aparells', create_report_aparells_view),
        ('report_supervisio', create_report_supervisio_view),
        ('report_habitacions', create_report_habitacions_view),
        ('report_metge', create_report_metge_view),
        ('report_pacient', create_report_pacient_view),
    ]

    for name, creator in all_views:
        frame, on_show = creator(container, app_state, navigate)
        frame.grid(row=0, column=0, sticky='nsew')
        views[name] = frame
        on_show_callbacks[name] = on_show

    navigate('login')
    root.mainloop()


if __name__ == '__main__':
    main()
