import tkinter as tk
from tkinter import ttk

from .. import api_client as api
from .base import clear_tree


def create_report_visites_dia_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    card = ttk.Frame(frame, style='Card.TFrame', padding=20)
    card.grid(row=0, column=0, sticky='nsew', padx=16, pady=16)
    card.columnconfigure(0, weight=1)
    card.rowconfigure(4, weight=1)

    ttk.Label(card, text='Visites per Dia', style='Title.TLabel').grid(row=0, column=0, sticky='w')
    ttk.Label(card, text="Consulta el total de visites d'una data concreta.", style='Muted.TLabel').grid(row=1, column=0, sticky='w', pady=(4, 8))

    controls = ttk.Frame(card)
    controls.grid(row=2, column=0, sticky='we', pady=(0, 8))

    ttk.Label(controls, text='Data').grid(row=0, column=0, sticky='w')
    date_entry = ttk.Entry(controls, width=14)
    date_entry.grid(row=0, column=1, sticky='w', padx=(8, 16))

    ttk.Button(controls, text='Cargar', style='Primary.TButton', command=lambda: load_data()).grid(row=0, column=2, sticky='w')
    ttk.Button(controls, text='Volver', command=lambda: navigate('home')).grid(row=0, column=3, sticky='w', padx=(8, 0))

    message_var = tk.StringVar(value='Selecciona una data per carregar el resum.')
    ttk.Label(card, textvariable=message_var, style='Muted.TLabel').grid(row=3, column=0, sticky='w', pady=(0, 8))

    cols = ('data_visita', 'total_visites')
    tree = ttk.Treeview(card, columns=cols, show='headings', height=18)
    tree.heading('data_visita', text='Dia')
    tree.heading('total_visites', text='Total visites')
    tree.column('data_visita', width=140, anchor='center')
    tree.column('total_visites', width=160, anchor='center')
    tree.grid(row=4, column=0, sticky='nsew')

    scrollbar = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
    scrollbar.grid(row=4, column=1, sticky='ns')
    tree.configure(yscrollcommand=scrollbar.set)

    def load_data():
        date_value = date_entry.get().strip()

        if not date_value:
            message_var.set('Selecciona una data.')
            return

        clear_tree(tree)
        payload = api.get_visites_dia(date_value)

        rows = payload.get('data') or []

        if not rows:
            message_var.set('No hi ha visites per a aquest dia.')
            return

        for row in rows:
            tree.insert('', 'end', values=(
                row.get('data_visita') or '-',
                row.get('total_visites') or 0,
            ))

        message_var.set('Informe carregat correctament.')

    def on_show():
        date_entry.delete(0, tk.END)
        message_var.set('Selecciona una data per carregar el resum.')
        clear_tree(tree)

    return frame, on_show