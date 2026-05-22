import tkinter as tk
from tkinter import filedialog, ttk

from .. import api_client as api
from .base import clear_tree


def create_report_visites_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    card = ttk.Frame(frame, style='Card.TFrame', padding=20)
    card.grid(row=0, column=0, sticky='nsew', padx=16, pady=16)
    card.columnconfigure(0, weight=1)
    card.rowconfigure(5, weight=1)

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

    export_frame = ttk.LabelFrame(card, text='Exportación de datos', padding=12)
    export_frame.grid(row=2, column=0, sticky='we', pady=(0, 8))
    for column in range(4):
        export_frame.columnconfigure(column, weight=1)

    ttk.Button(export_frame, text='Descargar JSON', command=lambda: download_export('json')).grid(row=0, column=0, sticky='we', padx=(0, 6), pady=(0, 6))
    ttk.Button(export_frame, text='Descargar XML', command=lambda: download_export('xml')).grid(row=0, column=1, sticky='we', padx=6, pady=(0, 6))
    ttk.Button(export_frame, text='JSON Schema', command=lambda: download_schema('json')).grid(row=0, column=2, sticky='we', padx=6, pady=(0, 6))
    ttk.Button(export_frame, text='XSD', command=lambda: download_schema('xml')).grid(row=0, column=3, sticky='we', padx=(6, 0), pady=(0, 6))

    message_var = tk.StringVar(value='Carrega el informe per defecte o filtra per dates.')
    ttk.Label(card, textvariable=message_var, style='Muted.TLabel').grid(row=3, column=0, sticky='w', pady=(0, 8))

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
    tree.grid(row=5, column=0, sticky='nsew')

    scrollbar = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
    scrollbar.grid(row=5, column=1, sticky='ns')
    tree.configure(yscrollcommand=scrollbar.set)

    def resolve_date_range():
        date_value = date_entry.get().strip()
        end_date_value = end_date_entry.get().strip()

        if not date_value and not end_date_value:
            return '', ''

        start_date = date_value or end_date_value
        end_date = end_date_value or start_date

        if start_date and end_date and start_date > end_date:
            raise ValueError('La fecha de inicio debe ser anterior o igual a la fecha de fin.')

        return start_date, end_date

    def build_export_filename(extension, start_date, end_date):
        if start_date and end_date:
            date_segment = start_date if start_date == end_date else f'{start_date}_{end_date}'
            return f'visites_{date_segment}.{extension}'
        return f'visites.{extension}'

    def save_content(default_name, extension, file_types, content):
        file_path = filedialog.asksaveasfilename(
            title='Guardar exportación',
            initialfile=default_name,
            defaultextension=f'.{extension}',
            filetypes=file_types,
        )

        if not file_path:
            return False

        with open(file_path, 'wb') as output_file:
            output_file.write(content)

        return True

    def download_export(export_format):
        try:
            start_date, end_date = resolve_date_range()
        except ValueError as exc:
            message_var.set(str(exc))
            return

        extension = 'json' if export_format == 'json' else 'xml'
        file_types = [('JSON files', '*.json')] if export_format == 'json' else [('XML files', '*.xml')]

        try:
            content = api.download_visites_export(export_format, start_date or None, end_date or None)
        except Exception as exc:
            message_var.set(str(exc))
            return

        if save_content(build_export_filename(extension, start_date, end_date), extension, file_types, content):
            message_var.set(f'Exportación {extension.upper()} guardada correctamente.')

    def download_schema(schema_format):
        extension = 'schema.json' if schema_format == 'json' else 'xsd'
        default_name = 'visites_export.schema.json' if schema_format == 'json' else 'visites_export.xsd'
        file_types = [('JSON Schema', '*.json')] if schema_format == 'json' else [('XSD files', '*.xsd')]

        try:
            content = api.download_visites_schema(schema_format)
        except Exception as exc:
            message_var.set(str(exc))
            return

        if save_content(default_name, extension, file_types, content):
            message_var.set('Esquema guardado correctamente.')

    def load_data():
        try:
            date_value, end_date_value = resolve_date_range()
        except ValueError as exc:
            message_var.set(str(exc))
            return

        if not date_value and not end_date_value:
            clear_tree(tree)
            payload = api.get_visites()
        else:
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
