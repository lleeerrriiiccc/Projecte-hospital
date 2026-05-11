import tkinter as tk
from tkinter import ttk

from .. import api_client as api
from .base import clear_tree


def create_report_personal_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    card = ttk.Frame(frame, style='Card.TFrame', padding=20)
    card.grid(row=0, column=0, sticky='nsew', padx=16, pady=16)
    card.columnconfigure(0, weight=1)
    card.rowconfigure(3, weight=1)

    ttk.Label(card, text='Informe de Personal', style='Title.TLabel').grid(row=0, column=0, sticky='w')
    ttk.Label(card, text="Mostra tot el personal que treballa a l'hospital.", style='Muted.TLabel').grid(row=1, column=0, sticky='w', pady=(4, 8))

    controls = ttk.Frame(card)
    controls.grid(row=2, column=0, sticky='we', pady=(0, 8))
    ttk.Button(controls, text='Cargar', style='Primary.TButton', command=lambda: load_data()).grid(row=0, column=0, sticky='w')
    ttk.Button(controls, text='Volver', command=lambda: navigate('home')).grid(row=0, column=1, sticky='w', padx=(8, 0))

    message_var = tk.StringVar(value='Carga el informe de personal.')
    ttk.Label(card, textvariable=message_var, style='Muted.TLabel').grid(row=3, column=0, sticky='w', pady=(0, 8))

    cols = ('id_intern', 'nom_complet', 'tipus_feina', 'telefon', 'email', 'data_alta')
    tree = ttk.Treeview(card, columns=cols, show='headings', height=18)
    tree.heading('id_intern', text='ID')
    tree.heading('nom_complet', text='Nom complet')
    tree.heading('tipus_feina', text='Feina')
    tree.heading('telefon', text='Telefon')
    tree.heading('email', text='Email')
    tree.heading('data_alta', text='Alta')
    tree.column('id_intern', width=70, anchor='center')
    tree.column('nom_complet', width=260, anchor='w')
    tree.column('tipus_feina', width=120, anchor='center')
    tree.column('telefon', width=120, anchor='center')
    tree.column('email', width=240, anchor='w')
    tree.column('data_alta', width=110, anchor='center')
    tree.grid(row=4, column=0, sticky='nsew')

    scrollbar = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
    scrollbar.grid(row=4, column=1, sticky='ns')
    tree.configure(yscrollcommand=scrollbar.set)

    def load_data():
        clear_tree(tree)

        payload = api.get_personal_report()
        rows = payload.get('data') or []

        if not rows:
            message_var.set('No hi ha personal disponible.')
            return

        for row in rows:
            tree.insert('', 'end', values=(
                row.get('id_intern') or '-',
                row.get('nom_complet') or '-',
                row.get('tipus_feina') or '-',
                row.get('telefon') or '-',
                row.get('email') or '-',
                row.get('data_alta') or '-',
            ))

        message_var.set('Informe carregat correctament.')

    def on_show():
        message_var.set('Carga el informe de personal.')
        load_data()

    return frame, on_show