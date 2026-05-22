import tkinter as tk
from tkinter import ttk

from .. import api_client as api
from .base import today_iso, parse_iso_date, clear_tree


def create_report_quirofans_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    card = ttk.Frame(frame, style='Card.TFrame', padding=20)
    card.grid(row=0, column=0, sticky='nsew', padx=16, pady=16)
    card.columnconfigure(0, weight=1)
    card.rowconfigure(3, weight=1)

    ttk.Label(card, text='Informe de Quirofans', style='Title.TLabel').grid(row=0, column=0, sticky='w')

    controls = ttk.Frame(card)
    controls.grid(row=1, column=0, sticky='we', pady=(10, 8))

    ttk.Label(controls, text='Fecha (YYYY-MM-DD)').grid(row=0, column=0, sticky='w')
    date_entry = ttk.Entry(controls, width=16)
    date_entry.grid(row=0, column=1, sticky='w', padx=(8, 8))
    date_entry.insert(0, today_iso())

    ttk.Button(controls, text='Cargar', style='Primary.TButton', command=lambda: load_data()).grid(row=0, column=2, sticky='w')
    ttk.Button(controls, text='Volver', command=lambda: navigate('home')).grid(row=0, column=3, sticky='w', padx=(8, 0))

    message_var = tk.StringVar(value='Selecciona una fecha para cargar quirofans.')
    ttk.Label(card, textvariable=message_var, style='Muted.TLabel').grid(row=2, column=0, sticky='w', pady=(0, 8))

    cols = ('id_operacio', 'hora_operacio', 'procediment', 'pacient', 'metge')
    tree = ttk.Treeview(card, columns=cols, show='headings', height=18)
    tree.heading('id_operacio', text='ID')
    tree.heading('hora_operacio', text='Hora')
    tree.heading('procediment', text='Procediment')
    tree.heading('pacient', text='Pacient')
    tree.heading('metge', text='Metge')
    tree.column('id_operacio', width=70, anchor='center')
    tree.column('hora_operacio', width=90, anchor='center')
    tree.column('procediment', width=240, anchor='w')
    tree.column('pacient', width=190, anchor='w')
    tree.column('metge', width=190, anchor='w')
    tree.grid(row=3, column=0, sticky='nsew')

    scrollbar = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
    scrollbar.grid(row=3, column=1, sticky='ns')
    tree.configure(yscrollcommand=scrollbar.set)

    def load_data():
        date_value = date_entry.get().strip()
        try:
            parse_iso_date(date_value, 'Formato de fecha invalido. Usa YYYY-MM-DD.')
        except ValueError as exc:
            message_var.set(str(exc))
            return

        clear_tree(tree)

        try:
            payload = api.get_report('quirofans', params={'date': date_value})
            rows = payload.get('data') or []

            if not rows:
                message_var.set('No hay operaciones para esta fecha.')
                return

            for row in rows:
                if not isinstance(row, dict):
                    continue
                tree.insert('', 'end', values=(
                    row.get('id_operacio') or '-',
                    row.get('hora_operacio') or '-',
                    row.get('procediment') or '-',
                    row.get('pacient') or '-',
                    row.get('metge') or '-',
                ))

            message_var.set('Informe cargado correctamente.')
        except Exception as exc:
            message_var.set(str(exc))

    def on_show():
        message_var.set('Selecciona una fecha para cargar quirofans.')

    return frame, on_show
