import tkinter as tk
from tkinter import ttk

from .. import api_client as api
from .base import clear_tree


def create_report_supervisio_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    card = ttk.Frame(frame, style='Card.TFrame', padding=20)
    card.grid(row=0, column=0, sticky='nsew', padx=16, pady=16)
    card.columnconfigure(0, weight=1)
    card.rowconfigure(3, weight=1)

    ttk.Label(card, text='Informe de Supervisio', style='Title.TLabel').grid(row=0, column=0, sticky='w')

    controls = ttk.Frame(card)
    controls.grid(row=1, column=0, sticky='we', pady=(10, 8))
    ttk.Button(controls, text='Cargar', style='Primary.TButton', command=lambda: load_data()).grid(row=0, column=0, sticky='w')
    ttk.Button(controls, text='Volver', command=lambda: navigate('home')).grid(row=0, column=1, sticky='w', padx=(8, 0))

    message_var = tk.StringVar(value='Carga el informe de supervisio.')
    ttk.Label(card, textvariable=message_var, style='Muted.TLabel').grid(row=2, column=0, sticky='w', pady=(0, 8))

    tree = ttk.Treeview(card, columns=('metge', 'infermeres'), show='headings', height=18)
    tree.heading('metge', text='Metge supervisor')
    tree.heading('infermeres', text='Infermeres')
    tree.column('metge', width=260, anchor='w')
    tree.column('infermeres', width=600, anchor='w')
    tree.grid(row=3, column=0, sticky='nsew')

    scrollbar = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
    scrollbar.grid(row=3, column=1, sticky='ns')
    tree.configure(yscrollcommand=scrollbar.set)

    def load_data():
        clear_tree(tree)

        try:
            payload = api.get_report('supervisio')
            rows = payload.get('data') or []

            if not rows:
                message_var.set('No hay datos de supervisio.')
                return

            for row in rows:
                doctor = row[0] if isinstance(row, (list, tuple)) and len(row) > 0 else ''
                nurses = row[1] if isinstance(row, (list, tuple)) and len(row) > 1 else ''
                tree.insert('', 'end', values=(doctor or 'Caps de planta (sense supervisor)', nurses or '-'))

            message_var.set('Informe cargado correctamente.')
        except Exception as exc:
            message_var.set(str(exc))

    def on_show():
        message_var.set('Carga el informe de supervisio.')

    return frame, on_show
