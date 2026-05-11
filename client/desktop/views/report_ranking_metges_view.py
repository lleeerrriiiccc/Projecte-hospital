import tkinter as tk
from tkinter import ttk

from .. import api_client as api
from .base import clear_tree


def create_report_ranking_metges_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    card = ttk.Frame(frame, style='Card.TFrame', padding=20)
    card.grid(row=0, column=0, sticky='nsew', padx=16, pady=16)
    card.columnconfigure(0, weight=1)
    card.rowconfigure(3, weight=1)

    ttk.Label(card, text='Ranking de Metges', style='Title.TLabel').grid(row=0, column=0, sticky='w')
    ttk.Label(card, text='Mostra els metges que han atès més pacients.', style='Muted.TLabel').grid(row=1, column=0, sticky='w', pady=(4, 8))

    controls = ttk.Frame(card)
    controls.grid(row=2, column=0, sticky='we', pady=(0, 8))
    ttk.Button(controls, text='Cargar', style='Primary.TButton', command=lambda: load_data()).grid(row=0, column=0, sticky='w')
    ttk.Button(controls, text='Volver', command=lambda: navigate('home')).grid(row=0, column=1, sticky='w', padx=(8, 0))

    message_var = tk.StringVar(value='Carga el ranking de metges.')
    ttk.Label(card, textvariable=message_var, style='Muted.TLabel').grid(row=3, column=0, sticky='w', pady=(0, 8))

    cols = ('metge', 'pacients_atesos', 'total_visites')
    tree = ttk.Treeview(card, columns=cols, show='headings', height=18)
    tree.heading('metge', text='Metge')
    tree.heading('pacients_atesos', text='Pacients atesos')
    tree.heading('total_visites', text='Total visites')
    tree.column('metge', width=360, anchor='w')
    tree.column('pacients_atesos', width=160, anchor='center')
    tree.column('total_visites', width=140, anchor='center')
    tree.grid(row=4, column=0, sticky='nsew')

    scrollbar = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
    scrollbar.grid(row=4, column=1, sticky='ns')
    tree.configure(yscrollcommand=scrollbar.set)

    def load_data():
        clear_tree(tree)

        payload = api.get_ranking_metges_report()
        rows = payload.get('data') or []

        if not rows:
            message_var.set('No hi ha dades de metges.')
            return

        for row in rows:
            tree.insert('', 'end', values=(
                row.get('metge') or '-',
                row.get('pacients_atesos') or 0,
                row.get('total_visites') or 0,
            ))

        message_var.set('Informe carregat correctament.')

    def on_show():
        message_var.set('Carga el ranking de metges.')
        load_data()

    return frame, on_show