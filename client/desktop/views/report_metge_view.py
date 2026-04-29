import tkinter as tk
from tkinter import ttk

from .. import api_client as api
from .base import today_iso, parse_iso_date, clear_tree, build_options_map, build_combo_values, split_combo_value


def create_report_metge_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    card = ttk.Frame(frame, style='Card.TFrame', padding=20)
    card.grid(row=0, column=0, sticky='nsew', padx=16, pady=16)
    card.columnconfigure(0, weight=1)
    card.rowconfigure(4, weight=1)
    card.rowconfigure(6, weight=1)

    ttk.Label(card, text='Informe Horari de Metge', style='Title.TLabel').grid(row=0, column=0, sticky='w')

    controls = ttk.Frame(card)
    controls.grid(row=1, column=0, sticky='we', pady=(10, 8))

    ttk.Label(controls, text='Metge').grid(row=0, column=0, sticky='w')
    doctor_combo = ttk.Combobox(controls, state='readonly', width=32)
    doctor_combo.grid(row=0, column=1, sticky='w', padx=(8, 14))

    ttk.Label(controls, text='Fecha (YYYY-MM-DD)').grid(row=0, column=2, sticky='w')
    date_entry = ttk.Entry(controls, width=16)
    date_entry.grid(row=0, column=3, sticky='w', padx=(8, 8))
    date_entry.insert(0, today_iso())

    ttk.Button(controls, text='Cargar', style='Primary.TButton', command=lambda: load_data()).grid(row=0, column=4, sticky='w')
    ttk.Button(controls, text='Volver', command=lambda: navigate('home')).grid(row=0, column=5, sticky='w', padx=(8, 0))

    message_var = tk.StringVar(value='Selecciona metge y fecha para consultar.')
    ttk.Label(card, textvariable=message_var, style='Muted.TLabel').grid(row=2, column=0, sticky='w', pady=(0, 8))

    stats_frame = ttk.Frame(card)
    stats_frame.grid(row=3, column=0, sticky='we', pady=(0, 8))
    stats_frame.columnconfigure((0, 1, 2), weight=1)

    occupied_var = tk.StringVar(value='Franges ocupades: 0')
    free_var = tk.StringVar(value='Franges lliures: 25')
    events_var = tk.StringVar(value='Actes del dia: 0')

    ttk.Label(stats_frame, textvariable=occupied_var, style='Muted.TLabel').grid(row=0, column=0, sticky='w')
    ttk.Label(stats_frame, textvariable=free_var, style='Muted.TLabel').grid(row=0, column=1, sticky='w')
    ttk.Label(stats_frame, textvariable=events_var, style='Muted.TLabel').grid(row=0, column=2, sticky='w')

    timeline_frame = ttk.Frame(card)
    timeline_frame.grid(row=4, column=0, sticky='nsew', pady=(0, 8))
    timeline_frame.columnconfigure(0, weight=1)
    timeline_frame.rowconfigure(1, weight=1)

    ttk.Label(timeline_frame, text='Calendari diari', style='Muted.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 4))

    tl_cols = ('hora', 'estat', 'detall')
    timeline_tree = ttk.Treeview(timeline_frame, columns=tl_cols, show='headings', height=9)
    timeline_tree.heading('hora', text='Hora')
    timeline_tree.heading('estat', text='Estat')
    timeline_tree.heading('detall', text='Detall')
    timeline_tree.column('hora', width=90, anchor='center')
    timeline_tree.column('estat', width=110, anchor='center')
    timeline_tree.column('detall', width=580, anchor='w')
    timeline_tree.grid(row=1, column=0, sticky='nsew')

    tl_scrollbar = ttk.Scrollbar(timeline_frame, orient='vertical', command=timeline_tree.yview)
    tl_scrollbar.grid(row=1, column=1, sticky='ns')
    timeline_tree.configure(yscrollcommand=tl_scrollbar.set)

    cols = ('hora', 'tipus', 'pacient', 'detall')
    tree = ttk.Treeview(card, columns=cols, show='headings', height=17)
    tree.heading('hora', text='Hora')
    tree.heading('tipus', text='Tipus')
    tree.heading('pacient', text='Pacient')
    tree.heading('detall', text='Detall')
    tree.column('hora', width=100, anchor='center')
    tree.column('tipus', width=90, anchor='center')
    tree.column('pacient', width=210, anchor='w')
    tree.column('detall', width=380, anchor='w')
    tree.grid(row=6, column=0, sticky='nsew')

    scrollbar = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
    scrollbar.grid(row=6, column=1, sticky='ns')
    tree.configure(yscrollcommand=scrollbar.set)

    metges_map = {}

    def normalize_hour(value):
        text = str(value or '')
        if not text:
            return ''
        parts = text.split(':')
        if len(parts) < 2:
            return ''
        try:
            return f'{int(parts[0]):02d}:00'
        except ValueError:
            return ''

    def render_timeline(rows):
        clear_tree(timeline_tree)

        grouped = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            hour_key = normalize_hour(row.get('hora'))
            if not hour_key:
                continue
            grouped.setdefault(hour_key, []).append(row)

        occupied = len(grouped)
        free = 25 - occupied
        occupied_var.set(f'Franges ocupades: {occupied}')
        free_var.set(f'Franges lliures: {free}')
        events_var.set(f'Actes del dia: {len(rows)}')

        for hour in range(25):
            hour_key = f'{hour:02d}:00'
            events = grouped.get(hour_key, [])
            if events:
                details = []
                for event in events:
                    event_type = str(event.get('tipus') or 'acte')
                    patient = str(event.get('pacient') or '-')
                    detail = str(event.get('detall') or '-')
                    details.append(f'{event_type}: {patient} ({detail})')
                timeline_tree.insert('', 'end', values=(hour_key, 'Ocupat', ' | '.join(details)))
            else:
                timeline_tree.insert('', 'end', values=(hour_key, 'Lliure', 'Sense actes'))

    def load_metges():
        payload = api.get_metges()
        rows = payload.get('data') or []
        loaded = build_options_map(rows, ['id_intern', 'id'], ['nom_complet', 'nom'])
        metges_map.clear()
        metges_map.update(loaded)
        values = build_combo_values(metges_map)
        doctor_combo.configure(values=values)
        if values and not doctor_combo.get():
            doctor_combo.set(values[0])

    def load_data():
        doctor_value = doctor_combo.get().strip()
        date_value = date_entry.get().strip()

        if not doctor_value:
            message_var.set('Selecciona un metge.')
            return

        try:
            parse_iso_date(date_value, 'Formato de fecha invalido. Usa YYYY-MM-DD.')
        except ValueError as exc:
            message_var.set(str(exc))
            return

        doctor_id = split_combo_value(doctor_value)
        clear_tree(tree)
        clear_tree(timeline_tree)
        occupied_var.set('Franges ocupades: 0')
        free_var.set('Franges lliures: 25')
        events_var.set('Actes del dia: 0')

        try:
            payload = api.get_report('metge', params={'metge': doctor_id, 'date': date_value})
            rows = payload.get('data') or []

            if not rows:
                message_var.set('No hay agenda para este metge y fecha.')
                render_timeline([])
                return

            for row in rows:
                if not isinstance(row, dict):
                    continue
                tree.insert('', 'end', values=(
                    row.get('hora') or '-',
                    row.get('tipus') or '-',
                    row.get('pacient') or '-',
                    row.get('detall') or '-',
                ))

            message_var.set('Informe cargado correctamente.')
            render_timeline(rows)
        except Exception as exc:
            message_var.set(str(exc))

    def on_show():
        try:
            load_metges()
            message_var.set('Selecciona metge y fecha para consultar.')
        except Exception as exc:
            message_var.set(f'No se pudieron cargar metges: {exc}')

    return frame, on_show
