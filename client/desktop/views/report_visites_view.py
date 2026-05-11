import tkinter as tk
from tkinter import ttk

from .. import api_client as api
from .base import clear_tree


def create_report_visites_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    card = ttk.Frame(frame, style='Card.TFrame', padding=20)
    card.grid(row=0, column=0, sticky='nsew', padx=16, pady=16)
    card.columnconfigure(0, weight=1)
    card.rowconfigure(4, weight=1)

    ttk.Label(card, text='Informe de Visites', style='Title.TLabel').grid(row=0, column=0, sticky='w')

    controls = ttk.Frame(card)
    controls.grid(row=1, column=0, sticky='we', pady=(10, 8))

    ttk.Label(controls, text='Fecha inicio (YYYY-MM-DD)').grid(row=0, column=0, sticky='w')
    date_entry = ttk.Entry(controls, width=16)
    date_entry.grid(row=0, column=1, sticky='w', padx=(8, 8))

    ttk.Label(controls, text='Fecha fin').grid(row=0, column=2, sticky='w')
    end_date_entry = ttk.Entry(controls, width=16)
    end_date_entry.grid(row=0, column=3, sticky='w', padx=(8, 8))

    ttk.Button(controls, text='Cargar', style='Primary.TButton', command=lambda: load_data()).grid(row=0, column=4, sticky='w')
    ttk.Button(controls, text='Volver', command=lambda: navigate('home')).grid(row=0, column=5, sticky='w', padx=(8, 0))

    message_var = tk.StringVar(value='Carrega el informe per defecte o filtra per dates.')
    ttk.Label(card, textvariable=message_var, style='Muted.TLabel').grid(row=2, column=0, sticky='w', pady=(0, 8))

    cols = ('data_visita', 'hora', 'pacient', 'metge')
    tree = ttk.Treeview(card, columns=cols, show='headings', height=18)
    tree.heading('data_visita', text='Fecha')
    tree.heading('hora', text='Hora')
    tree.heading('pacient', text='Paciente')
    tree.heading('metge', text='Medico')
    tree.column('data_visita', width=120, anchor='center')
    tree.column('hora', width=120, anchor='center')
    tree.column('pacient', width=300, anchor='w')
    tree.column('metge', width=300, anchor='w')
    tree.grid(row=4, column=0, sticky='nsew')

    scrollbar = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
    scrollbar.grid(row=4, column=1, sticky='ns')
    tree.configure(yscrollcommand=scrollbar.set)

    def load_data():
        date_value = date_entry.get().strip()
        end_date_value = end_date_entry.get().strip()

        if not date_value and not end_date_value:
            clear_tree(tree)
            payload = api.get_visites()
        else:
            if not date_value:
                date_value = end_date_value

            if end_date_value and date_value > end_date_value:
                message_var.set('La fecha de inicio debe ser anterior o igual a la fecha de fin.')
                return

            clear_tree(tree)
            payload = api.get_visites(date_value, end_date_value or None)

        rows = payload.get('data') or []

        for row in rows:
            tree.insert('', 'end', values=(
                row.get('data_visita') or '-',
                row.get('hora_visita') or '-',
                row.get('pacient') or '-',
                row.get('metge') or '-',
            ))

        if not rows:
            message_var.set('No hay visitas para este filtro.')
        else:
            message_var.set('Informe cargado correctamente.')

    def on_show():
        date_entry.delete(0, tk.END)
        end_date_entry.delete(0, tk.END)
        message_var.set('Carregant informe per defecte...')
        load_data()

    return frame, on_show
