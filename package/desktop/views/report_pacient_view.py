import tkinter as tk
from tkinter import ttk

from .. import api_client as api
from .base import clear_tree, build_options_map, build_combo_values, split_combo_value


def create_report_pacient_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    card = ttk.Frame(frame, style='Card.TFrame', padding=20)
    card.grid(row=0, column=0, sticky='nsew', padx=16, pady=16)
    card.columnconfigure(0, weight=1)
    card.rowconfigure(4, weight=1)

    ttk.Label(card, text='Informe de Pacient', style='Title.TLabel').grid(row=0, column=0, sticky='w')

    controls = ttk.Frame(card)
    controls.grid(row=1, column=0, sticky='we', pady=(10, 8))

    ttk.Label(controls, text='Pacient').grid(row=0, column=0, sticky='w')
    patient_combo = ttk.Combobox(controls, state='readonly', width=40)
    patient_combo.grid(row=0, column=1, sticky='w', padx=(8, 8))

    ttk.Button(controls, text='Cargar', style='Primary.TButton', command=lambda: load_data()).grid(row=0, column=2, sticky='w')
    ttk.Button(controls, text='Volver', command=lambda: navigate('home')).grid(row=0, column=3, sticky='w', padx=(8, 0))

    message_var = tk.StringVar(value='Selecciona un pacient para ver su informe.')
    ttk.Label(card, textvariable=message_var, style='Muted.TLabel').grid(row=2, column=0, sticky='w', pady=(0, 8))

    summary_var = tk.StringVar(value='')
    ttk.Label(card, textvariable=summary_var, style='Muted.TLabel').grid(row=3, column=0, sticky='w', pady=(0, 8))

    cols = ('tipus', 'data_event', 'hora_event', 'descripcio', 'info_extra')
    tree = ttk.Treeview(card, columns=cols, show='headings', height=16)
    tree.heading('tipus', text='Tipus')
    tree.heading('data_event', text='Data')
    tree.heading('hora_event', text='Hora')
    tree.heading('descripcio', text='Descripcio')
    tree.heading('info_extra', text='Info extra')
    tree.column('tipus', width=120, anchor='center')
    tree.column('data_event', width=110, anchor='center')
    tree.column('hora_event', width=90, anchor='center')
    tree.column('descripcio', width=260, anchor='w')
    tree.column('info_extra', width=230, anchor='w')
    tree.grid(row=4, column=0, sticky='nsew')

    scrollbar = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
    scrollbar.grid(row=4, column=1, sticky='ns')
    tree.configure(yscrollcommand=scrollbar.set)

    patients_map = {}

    def load_patients():
        payload = api.get_pacients()
        rows = payload.get('data') or []
        loaded = build_options_map(rows, ['id_pacient', 'id'], ['nom_complet', 'nom'])
        patients_map.clear()
        patients_map.update(loaded)
        values = build_combo_values(patients_map)
        patient_combo.configure(values=values)
        if values and not patient_combo.get():
            patient_combo.set(values[0])

    def load_data():
        patient_value = patient_combo.get().strip()
        if not patient_value:
            message_var.set('Selecciona un pacient.')
            return

        patient_id = split_combo_value(patient_value)
        clear_tree(tree)

        try:
            payload = api.get_report('pacient', params={'pacient': patient_id})
            rows = payload.get('data') or []

            if not rows:
                summary_var.set('')
                message_var.set('No hay eventos para este pacient.')
                return

            by_type = {}
            for row in rows:
                if not isinstance(row, dict):
                    continue
                event_type = row.get('tipus') or 'desconegut'
                by_type[event_type] = by_type.get(event_type, 0) + 1
                tree.insert('', 'end', values=(
                    event_type,
                    row.get('data_event') or '-',
                    row.get('hora_event') or '-',
                    row.get('descripcio') or '-',
                    row.get('info_extra') or '-',
                ))

            summary = ', '.join([f'{k}: {v}' for k, v in sorted(by_type.items())])
            summary_var.set(f'Totals -> {summary}')
            message_var.set('Informe cargado correctamente.')
        except Exception as exc:
            summary_var.set('')
            message_var.set(str(exc))

    def on_show():
        summary_var.set('')
        try:
            load_patients()
            message_var.set('Selecciona un pacient para ver su informe.')
        except Exception as exc:
            message_var.set(f'No se pudieron cargar pacients: {exc}')

    return frame, on_show
