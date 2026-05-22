import tkinter as tk
from tkinter import ttk

from .. import api_client as api
from .base import clear_tree


def create_report_planta_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    card = ttk.Frame(frame, style='Card.TFrame', padding=20)
    card.grid(row=0, column=0, sticky='nsew', padx=16, pady=16)
    card.columnconfigure(0, weight=1)
    card.rowconfigure(3, weight=1)

    ttk.Label(card, text='Informe per Planta', style='Title.TLabel').grid(row=0, column=0, sticky='w')
    ttk.Label(card, text='Mostra habitacions, quiròfans i infermers per cada planta.', style='Muted.TLabel').grid(row=1, column=0, sticky='w', pady=(4, 8))

    controls = ttk.Frame(card)
    controls.grid(row=2, column=0, sticky='we', pady=(0, 8))
    ttk.Button(controls, text='Cargar', style='Primary.TButton', command=lambda: load_data()).grid(row=0, column=0, sticky='w')
    ttk.Button(controls, text='Volver', command=lambda: navigate('home')).grid(row=0, column=1, sticky='w', padx=(8, 0))

    message_var = tk.StringVar(value='Carga el informe per planta.')
    ttk.Label(card, textvariable=message_var, style='Muted.TLabel').grid(row=3, column=0, sticky='w', pady=(0, 8))

    cols = ('planta', 'habitacions', 'quirofans', 'infermeres')
    tree = ttk.Treeview(card, columns=cols, show='headings', height=18)
    tree.heading('planta', text='Planta')
    tree.heading('habitacions', text='Habitacions')
    tree.heading('quirofans', text='Quirofans')
    tree.heading('infermeres', text='Infermers')
    tree.column('planta', width=240, anchor='w')
    tree.column('habitacions', width=120, anchor='center')
    tree.column('quirofans', width=120, anchor='center')
    tree.column('infermeres', width=120, anchor='center')
    tree.grid(row=4, column=0, sticky='nsew')

    scrollbar = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
    scrollbar.grid(row=4, column=1, sticky='ns')
    tree.configure(yscrollcommand=scrollbar.set)

    def load_data():
        clear_tree(tree)

        payload = api.get_planta_report()
        rows = payload.get('data') or []

        if not rows:
            message_var.set('No hi ha dades de planta.')
            return

        for row in rows:
            tree.insert('', 'end', values=(
                row.get('planta') or '-',
                row.get('habitacions') or 0,
                row.get('quirofans') or 0,
                row.get('infermeres') or 0,
            ))

        message_var.set('Informe carregat correctament.')

    def on_show():
        message_var.set('Carga el informe per planta.')
        load_data()

    return frame, on_show