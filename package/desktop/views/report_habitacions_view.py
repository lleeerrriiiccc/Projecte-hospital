import datetime
import tkinter as tk
from tkinter import ttk

from .. import api_client as api
from .base import parse_iso_date, clear_tree, clear_text_widget, build_options_map


def create_report_habitacions_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    card = ttk.Frame(frame, style='Card.TFrame', padding=20)
    card.grid(row=0, column=0, sticky='nsew', padx=16, pady=16)
    card.columnconfigure(0, weight=1)
    card.rowconfigure(4, weight=1)
    card.rowconfigure(6, weight=1)

    ttk.Label(card, text="Informe d'Habitacions", style='Title.TLabel').grid(row=0, column=0, sticky='w')

    controls = ttk.Frame(card)
    controls.grid(row=1, column=0, sticky='we', pady=(10, 8))

    ttk.Label(controls, text='Habitacio').grid(row=0, column=0, sticky='w')
    room_combo = ttk.Combobox(controls, state='readonly', width=16)
    room_combo.grid(row=0, column=1, sticky='w', padx=(8, 14))

    ttk.Label(controls, text='Mes (YYYY-MM)').grid(row=0, column=2, sticky='w')
    month_entry = ttk.Entry(controls, width=12)
    month_entry.grid(row=0, column=3, sticky='w', padx=(8, 8))
    month_entry.insert(0, datetime.date.today().strftime('%Y-%m'))

    ttk.Button(controls, text='Cargar', style='Primary.TButton', command=lambda: load_data()).grid(row=0, column=4, sticky='w')
    ttk.Button(controls, text='Volver', command=lambda: navigate('home')).grid(row=0, column=5, sticky='w', padx=(8, 0))

    message_var = tk.StringVar(value='Selecciona habitacio y mes para consultar ocupacion.')
    ttk.Label(card, textvariable=message_var, style='Muted.TLabel').grid(row=2, column=0, sticky='w', pady=(0, 8))

    summary_var = tk.StringVar(value='')
    ttk.Label(card, textvariable=summary_var, style='Muted.TLabel').grid(row=3, column=0, sticky='w', pady=(0, 8))

    ttk.Label(card, text="Calendari d'ocupacio", style='Muted.TLabel').grid(row=4, column=0, sticky='w', pady=(0, 6))

    calendar_text = tk.Text(card, height=14, wrap='none', relief='solid', borderwidth=1, font=('Courier New', 10), background='#ffffff')
    calendar_text.grid(row=5, column=0, sticky='nsew')

    cal_scroll = ttk.Scrollbar(card, orient='vertical', command=calendar_text.yview)
    cal_scroll.grid(row=5, column=1, sticky='ns')
    calendar_text.configure(yscrollcommand=cal_scroll.set)

    cols = ('data_inici', 'data_fi', 'pacient')
    tree = ttk.Treeview(card, columns=cols, show='headings', height=8)
    tree.heading('data_inici', text='Data inici')
    tree.heading('data_fi', text='Data fi')
    tree.heading('pacient', text='Pacient')
    tree.column('data_inici', width=120, anchor='center')
    tree.column('data_fi', width=120, anchor='center')
    tree.column('pacient', width=460, anchor='w')
    tree.grid(row=6, column=0, sticky='nsew', pady=(8, 0))

    scrollbar = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
    scrollbar.grid(row=6, column=1, sticky='ns', pady=(8, 0))
    tree.configure(yscrollcommand=scrollbar.set)

    def to_date(value):
        try:
            return datetime.datetime.strptime(str(value), '%Y-%m-%d').date()
        except ValueError:
            return None

    def occupants_for_day(day_date, rows):
        occupants = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            start = to_date(row.get('data_inici'))
            end = to_date(row.get('data_fi'))
            if start is None or end is None:
                continue
            if start <= day_date <= end:
                occupants.append(str(row.get('pacient') or 'pacient'))
        return occupants

    def render_calendar(month_value, rows):
        clear_text_widget(calendar_text)

        year_int, month_int = int(month_value[:4]), int(month_value[5:7])
        first = datetime.date(year_int, month_int, 1)
        if month_int == 12:
            next_month = datetime.date(year_int + 1, 1, 1)
        else:
            next_month = datetime.date(year_int, month_int + 1, 1)

        last_day = (next_month - datetime.timedelta(days=1)).day
        offset = first.weekday()

        calendar_text.insert(tk.END, 'Dl  Dt  Dc  Dj  Dv  Ds  Dg\n')
        calendar_text.insert(tk.END, '-' * 48 + '\n')

        current_col = 0
        if offset > 0:
            calendar_text.insert(tk.END, '    ' * offset)
            current_col = offset

        for day in range(1, last_day + 1):
            day_date = datetime.date(year_int, month_int, day)
            occupants = occupants_for_day(day_date, rows)
            marker = '*' if occupants else ' '
            calendar_text.insert(tk.END, f'{day:02d}{marker} ')
            current_col += 1
            if current_col == 7:
                calendar_text.insert(tk.END, '\n')
                current_col = 0

        if current_col != 0:
            calendar_text.insert(tk.END, '\n')

        calendar_text.insert(tk.END, '\nLlegenda: * dia ocupat\n\n')
        for day in range(1, last_day + 1):
            day_date = datetime.date(year_int, month_int, day)
            occupants = occupants_for_day(day_date, rows)
            if occupants:
                calendar_text.insert(tk.END, f'{day:02d}: {", ".join(occupants)}\n')

        calendar_text.configure(state='disabled')

    def load_rooms():
        payload = api.get_habitacions()
        rows = payload.get('data') or []
        mapping = build_options_map(rows, ['num_habitacio', 'id'], ['num_habitacio', 'nom'])
        values = list(mapping.values())
        room_combo.configure(values=values)
        if values and not room_combo.get():
            room_combo.set(values[0])

    def load_data():
        room_value = room_combo.get().strip()
        month_value = month_entry.get().strip()

        if not room_value:
            message_var.set('Selecciona una habitacio.')
            return

        if not month_value:
            message_var.set('Selecciona un mes.')
            return

        try:
            parse_iso_date(month_value + '-01', 'El mes')
        except ValueError:
            message_var.set('Formato de mes invalido. Usa YYYY-MM.')
            return

        clear_tree(tree)
        clear_text_widget(calendar_text)
        calendar_text.configure(state='disabled')

        try:
            payload = api.get_report('habitacions', params={'habitacio': room_value})
            rows = payload.get('data') or []
            filtered = [row for row in rows if isinstance(row, dict) and
                        (str(row.get('data_inici') or '').startswith(month_value) or
                         str(row.get('data_fi') or '').startswith(month_value))]

            if not filtered:
                summary_var.set('')
                message_var.set('No hay ocupaciones para el filtro seleccionado.')
                render_calendar(month_value, [])
                return

            for row in filtered:
                tree.insert('', 'end', values=(
                    row.get('data_inici') or '-',
                    row.get('data_fi') or '-',
                    row.get('pacient') or '-',
                ))

            summary_var.set(f'Reservas: {len(filtered)}')
            message_var.set('Informe cargado correctamente.')
            render_calendar(month_value, filtered)
        except Exception as exc:
            summary_var.set('')
            message_var.set(str(exc))

    def on_show():
        summary_var.set('')
        try:
            load_rooms()
            message_var.set('Selecciona habitacio y mes para consultar ocupacion.')
        except Exception as exc:
            message_var.set(f'No se pudieron cargar habitacions: {exc}')

    return frame, on_show
