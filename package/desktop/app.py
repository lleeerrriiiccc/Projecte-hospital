import tkinter as tk
from tkinter import ttk

from . import api_client as api
from .config import WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH
from .theme import PALETTE
from .views.alta_pacient_view import create_alta_pacient_view
from .views.alta_personal_view import create_alta_personal_view
from .views.report_aparells_view import create_report_aparells_view
from .views.report_personal_view import create_report_personal_view
from .views.report_habitacions_view import create_report_habitacions_view
from .views.report_metge_view import create_report_metge_view
from .views.report_malalties_view import create_report_malalties_view
from .views.report_planta_view import create_report_planta_view
from .views.report_pacient_view import create_report_pacient_view
from .views.report_quirofans_view import create_report_quirofans_view
from .views.report_ranking_metges_view import create_report_ranking_metges_view
from .views.report_supervisio_view import create_report_supervisio_view
from .views.report_visites_dia_view import create_report_visites_dia_view
from .views.home_view import create_home_view
from .views.login_view import create_login_view
from .views.report_visites_view import create_report_visites_view


def setup_styles(root):
    style = ttk.Style(root)
    style.theme_use('clam')
    font_family = 'Bahnschrift'
    root.option_add('*Font', f'{font_family} 10')

    style.configure('App.TFrame', background=PALETTE['bg'])
    style.configure('Topbar.TFrame', background=PALETTE['primary'], relief='flat')
    style.configure('Card.TFrame', background=PALETTE['surface'], relief='solid', borderwidth=1)
    style.configure('AltCard.TFrame', background=PALETTE['surface_alt'], relief='solid', borderwidth=1)
    style.configure('Hero.TFrame', background=PALETTE['primary'], relief='flat')

    style.configure('TLabel', background=PALETTE['surface'], foreground=PALETTE['text'], font=(font_family, 10))
    style.configure('Title.TLabel', background=PALETTE['surface'], foreground=PALETTE['primary_dark'], font=(font_family, 20, 'bold'))
    style.configure('Subtitle.TLabel', background=PALETTE['surface'], foreground=PALETTE['muted'], font=(font_family, 10))
    style.configure('CardTitle.TLabel', background=PALETTE['surface'], foreground=PALETTE['primary_dark'], font=(font_family, 12, 'bold'))
    style.configure('CardBody.TLabel', background=PALETTE['surface'], foreground=PALETTE['muted'], font=(font_family, 10))
    style.configure('AltTitle.TLabel', background=PALETTE['surface_alt'], foreground=PALETTE['primary_dark'], font=(font_family, 12, 'bold'))
    style.configure('AltBody.TLabel', background=PALETTE['surface_alt'], foreground=PALETTE['muted'], font=(font_family, 10))
    style.configure('HeroTitle.TLabel', background=PALETTE['primary'], foreground=PALETTE['topbar_text'], font=(font_family, 24, 'bold'))
    style.configure('HeroBody.TLabel', background=PALETTE['primary'], foreground=PALETTE['topbar_text'], font=(font_family, 11))
    style.configure('HeroList.TLabel', background=PALETTE['primary'], foreground=PALETTE['topbar_text'], font=(font_family, 10))
    style.configure('HeroCaption.TLabel', background=PALETTE['primary'], foreground=PALETTE['primary_soft'], font=(font_family, 10, 'bold'))
    style.configure('TopbarTitle.TLabel', background=PALETTE['primary'], foreground=PALETTE['topbar_text'], font=(font_family, 17, 'bold'))
    style.configure('TopbarMuted.TLabel', background=PALETTE['primary'], foreground=PALETTE['topbar_text'], font=(font_family, 10))
    style.configure('Muted.TLabel', background=PALETTE['surface'], foreground=PALETTE['muted'], font=(font_family, 10))
    style.configure('Section.TLabel', background=PALETTE['surface'], foreground=PALETTE['primary_dark'], font=(font_family, 12, 'bold'))
    style.configure('Badge.TLabel', background=PALETTE['primary_soft'], foreground=PALETTE['primary_dark'], font=(font_family, 9, 'bold'), padding=(10, 4))
    style.configure('Status.TLabel', background=PALETTE['surface_alt'], foreground=PALETTE['text'], padding=(10, 8), font=(font_family, 10, 'bold'))
    style.configure('Error.TLabel', background=PALETTE['error_bg'], foreground=PALETTE['error_text'], padding=(10, 8), font=(font_family, 10, 'bold'))
    style.configure('Success.TLabel', background=PALETTE['success_bg'], foreground=PALETTE['success_text'], padding=(10, 8), font=(font_family, 10, 'bold'))

    style.configure('TEntry', fieldbackground='white', bordercolor=PALETTE['border'], lightcolor=PALETTE['border'], darkcolor=PALETTE['border'], foreground=PALETTE['text'], insertcolor=PALETTE['text'], padding=(10, 8))
    style.map('TEntry', bordercolor=[('focus', PALETTE['focus'])], lightcolor=[('focus', PALETTE['focus'])], darkcolor=[('focus', PALETTE['focus'])])
    style.configure('TCombobox', padding=(8, 6), fieldbackground='white', foreground=PALETTE['text'])
    style.configure('TCheckbutton', background=PALETTE['surface'], foreground=PALETTE['muted'], font=(font_family, 10))
    style.map('TCheckbutton', background=[('active', PALETTE['surface'])], foreground=[('active', PALETTE['text'])])
    style.configure('Inline.TCheckbutton', background=PALETTE['surface'], foreground=PALETTE['muted'], font=(font_family, 10))
    style.map('Inline.TCheckbutton', background=[('active', PALETTE['surface'])], foreground=[('active', PALETTE['text'])])

    style.configure('TButton', font=(font_family, 10, 'bold'), padding=(12, 10), borderwidth=0)
    style.configure('Primary.TButton', foreground='white', background=PALETTE['primary'], borderwidth=0)
    style.map('Primary.TButton', background=[('active', PALETTE['primary_dark']), ('pressed', PALETTE['primary_dark']), ('disabled', PALETTE['border'])], foreground=[('disabled', PALETTE['surface'])])
    style.configure('Secondary.TButton', foreground=PALETTE['text'], background=PALETTE['secondary_bg'], borderwidth=0)
    style.map('Secondary.TButton', background=[('active', PALETTE['secondary_active']), ('pressed', PALETTE['secondary_active']), ('disabled', PALETTE['border'])], foreground=[('disabled', PALETTE['muted'])])
    style.configure('Danger.TButton', foreground='white', background=PALETTE['danger'], borderwidth=0)
    style.map('Danger.TButton', background=[('active', PALETTE['danger_dark']), ('pressed', PALETTE['danger_dark']), ('disabled', PALETTE['border'])], foreground=[('disabled', PALETTE['surface'])])
    style.configure('Topbar.TButton', foreground=PALETTE['primary_dark'], background=PALETTE['topbar_text'], borderwidth=0, padding=(10, 6))
    style.map('Topbar.TButton', background=[('active', '#dce9f1'), ('pressed', '#dce9f1')], foreground=[('active', PALETTE['primary_dark'])])

    style.configure('Treeview', rowheight=32, font=(font_family, 10), fieldbackground='white', background='white', foreground=PALETTE['text'], bordercolor=PALETTE['border'])
    style.map('Treeview', background=[('selected', PALETTE['primary_soft'])], foreground=[('selected', PALETTE['text'])])
    style.configure('Treeview.Heading', font=(font_family, 10, 'bold'), background=PALETTE['primary'], foreground='white')


def main():
    root = tk.Tk()
    root.title('Hospital Tenso')
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
        ('report_planta', create_report_planta_view),
        ('report_personal', create_report_personal_view),
        ('report_malalties', create_report_malalties_view),
        ('report_ranking_metges', create_report_ranking_metges_view),
        ('report_visites_dia', create_report_visites_dia_view),
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
