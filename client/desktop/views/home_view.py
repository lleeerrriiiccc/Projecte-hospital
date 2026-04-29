import tkinter as tk
from tkinter import ttk

from .. import api_client as api


def create_home_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(1, weight=1)

    topbar = ttk.Frame(frame, style='Topbar.TFrame', padding=(18, 12))
    topbar.grid(row=0, column=0, sticky='we')
    topbar.columnconfigure(0, weight=1)

    ttk.Label(topbar, text='Gestio Hospitalaria', style='TopbarTitle.TLabel').grid(row=0, column=0, sticky='w')

    user_label = ttk.Label(topbar, text='', style='TopbarMuted.TLabel')
    user_label.grid(row=0, column=1, sticky='e')

    main = ttk.Frame(frame, padding=16)
    main.grid(row=1, column=0, sticky='nsew')
    main.columnconfigure(0, weight=1)

    card = ttk.Frame(main, style='Card.TFrame', padding=18)
    card.grid(row=0, column=0, sticky='nsew')
    card.columnconfigure(0, weight=1)

    ttk.Label(card, text='Panell principal', style='Title.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 10))

    # Seccions de navegació agrupades per àrea
    sections = [
        ('Pacients', [
            ('Nou pacient', lambda: navigate('alta_pacient')),
            ('Informe pacient', lambda: navigate('report_pacient')),
        ]),
        ('Enfermeria', [
            ('Informe supervisio', lambda: navigate('report_supervisio')),
        ]),
        ('Personal', [
            ('Nou personal', lambda: navigate('alta_personal')),
        ]),
        ('Visites', [
            ('Veure visites', lambda: navigate('report_visites')),
            ('Horari metge', lambda: navigate('report_metge')),
        ]),
        ('Quirofans', [
            ('Veure quirofans', lambda: navigate('report_quirofans')),
            ('Aparells', lambda: navigate('report_aparells')),
        ]),
        ('Habitacions', [
            ('Veure ocupacio', lambda: navigate('report_habitacions')),
        ]),
    ]

    row = 1
    for section_title, section_actions in sections:
        ttk.Label(card, text=section_title, style='Section.TLabel').grid(row=row, column=0, sticky='w', pady=(12, 4))
        row += 1
        for label, command in section_actions:
            ttk.Button(card, text=label, command=command, style='Primary.TButton').grid(row=row, column=0, sticky='we', pady=4)
            row += 1

    ttk.Separator(card, orient='horizontal').grid(row=row, column=0, sticky='we', pady=(12, 8))
    row += 1

    def logout():
        try:
            api.logout()
        except Exception:
            pass
        app_state['username'] = None
        app_state['role'] = None
        navigate('login')

    ttk.Button(card, text='Tancar sessio', command=logout, style='Secondary.TButton').grid(row=row, column=0, sticky='we')

    def on_show():
        username = app_state.get('username') or '-'
        user_label.configure(text=f'Hola, {username}')

    return frame, on_show
