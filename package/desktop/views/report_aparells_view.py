import tkinter as tk
from tkinter import ttk

from .. import api_client as api
from .base import clear_tree, clear_text_widget


def create_report_aparells_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    card = ttk.Frame(frame, style='Card.TFrame', padding=20)
    card.grid(row=0, column=0, sticky='nsew', padx=16, pady=16)
    card.columnconfigure(0, weight=1)
    card.rowconfigure(4, weight=1)
    card.rowconfigure(6, weight=1)

    ttk.Label(card, text="Informe d'Aparells", style='Title.TLabel').grid(row=0, column=0, sticky='w')

    controls = ttk.Frame(card)
    controls.grid(row=1, column=0, sticky='we', pady=(10, 8))
    ttk.Button(controls, text='Cargar', style='Primary.TButton', command=lambda: load_data()).grid(row=0, column=0, sticky='w')
    ttk.Button(controls, text='Volver', command=lambda: navigate('home')).grid(row=0, column=1, sticky='w', padx=(8, 0))

    message_var = tk.StringVar(value='Carga el informe de aparells.')
    ttk.Label(card, textvariable=message_var, style='Muted.TLabel').grid(row=2, column=0, sticky='w', pady=(0, 8))

    summary = ttk.Frame(card)
    summary.grid(row=3, column=0, sticky='we', pady=(0, 8))
    summary.columnconfigure((0, 1), weight=1)

    rooms_var = tk.StringVar(value='Quirofans: 0')
    machines_var = tk.StringVar(value='Maquines totals: 0')
    ttk.Label(summary, textvariable=rooms_var, style='Muted.TLabel').grid(row=0, column=0, sticky='w')
    ttk.Label(summary, textvariable=machines_var, style='Muted.TLabel').grid(row=0, column=1, sticky='w')

    cards_text = tk.Text(card, height=8, wrap='word', relief='solid', borderwidth=1, background='#ffffff')
    cards_text.grid(row=4, column=0, sticky='nsew', pady=(0, 8))

    cards_scroll = ttk.Scrollbar(card, orient='vertical', command=cards_text.yview)
    cards_scroll.grid(row=4, column=1, sticky='ns', pady=(0, 8))
    cards_text.configure(yscrollcommand=cards_scroll.set)

    cols = ('id_quirofan', 'planta', 'maquinari')
    tree = ttk.Treeview(card, columns=cols, show='headings', height=18)
    tree.heading('id_quirofan', text='Quirofan')
    tree.heading('planta', text='Planta')
    tree.heading('maquinari', text='Maquinari')
    tree.column('id_quirofan', width=110, anchor='center')
    tree.column('planta', width=110, anchor='center')
    tree.column('maquinari', width=620, anchor='w')
    tree.grid(row=6, column=0, sticky='nsew')

    scrollbar = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
    scrollbar.grid(row=6, column=1, sticky='ns')
    tree.configure(yscrollcommand=scrollbar.set)

    def render_cards(rows):
        cards_text.configure(state='normal')
        cards_text.delete('1.0', tk.END)

        total_machines = 0
        for row in rows:
            if not isinstance(row, dict):
                continue
            raw = str(row.get('maquinari') or '')
            machines = [item.strip() for item in raw.split(',') if item.strip()]
            total_machines += len(machines)

            room = row.get('id_quirofan') or '-'
            floor = row.get('planta') or '-'
            machines_text = ', '.join(machines) if machines else 'Sense aparells'
            cards_text.insert(tk.END, f'Quirofan {room} · Planta {floor}\n{len(machines)} maquines: {machines_text}\n\n')

        rooms_var.set(f'Quirofans: {len(rows)}')
        machines_var.set(f'Maquines totals: {total_machines}')
        cards_text.configure(state='disabled')

    def load_data():
        clear_tree(tree)
        clear_text_widget(cards_text)
        cards_text.configure(state='disabled')
        rooms_var.set('Quirofans: 0')
        machines_var.set('Maquines totals: 0')

        try:
            payload = api.get_report('aparells')
            rows = payload.get('data') or []

            if not rows:
                message_var.set('No hay datos de aparells.')
                return

            render_cards(rows)

            for row in rows:
                if isinstance(row, dict):
                    values = (row.get('id_quirofan') or '-', row.get('planta') or '-', row.get('maquinari') or '-')
                else:
                    values = ('-', '-', str(row))
                tree.insert('', 'end', values=values)

            message_var.set('Informe cargado correctamente.')
        except Exception as exc:
            message_var.set(str(exc))

    def on_show():
        message_var.set('Carga el informe de aparells.')

    return frame, on_show
