import tkinter as tk
from tkinter import messagebox, ttk

from .. import api_client as api
from ..theme import PALETTE


def create_home_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(1, weight=1)

    topbar = ttk.Frame(frame, style='Topbar.TFrame', padding=(18, 12))
    topbar.grid(row=0, column=0, sticky='we')
    topbar.columnconfigure(0, weight=1)

    ttk.Label(topbar, text='Gestio Hospitalaria', style='TopbarTitle.TLabel').grid(row=0, column=0, sticky='w')

    user_label = ttk.Label(topbar, text='', style='TopbarMuted.TLabel')
    user_label.grid(row=0, column=1, sticky='e')

    main = ttk.Frame(frame, style='App.TFrame')
    main.grid(row=1, column=0, sticky='nsew')
    main.columnconfigure(0, weight=1)
    main.rowconfigure(0, weight=1)

    canvas = tk.Canvas(main, background=PALETTE['bg'], borderwidth=0, highlightthickness=0)
    canvas.grid(row=0, column=0, sticky='nsew', padx=(16, 0), pady=16)

    scrollbar = ttk.Scrollbar(main, orient='vertical', command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky='ns', padx=(8, 16), pady=16)

    canvas.configure(yscrollcommand=scrollbar.set)

    card = ttk.Frame(canvas, style='Card.TFrame', padding=18)
    card.columnconfigure(0, weight=1)
    card_window = canvas.create_window((0, 0), window=card, anchor='nw')

    def sync_scroll_region(_event=None):
        canvas.configure(scrollregion=canvas.bbox('all'))

    def sync_card_width(event):
        canvas.itemconfigure(card_window, width=max(event.width, 100))

    card.bind('<Configure>', sync_scroll_region)
    canvas.bind('<Configure>', sync_card_width)

    ttk.Label(card, text='Panell principal', style='Title.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 10))

    # Seccions de navegació agrupades per àrea
    sections = [
        ('Consultes i informes', [
            ('Informe per planta', lambda: navigate('report_planta')),
            ('Informe personal', lambda: navigate('report_personal')),
            ('Malalties més comunes', lambda: navigate('report_malalties')),
            ('Ranking de metges', lambda: navigate('report_ranking_metges')),
            ('Visites per dia', lambda: navigate('report_visites_dia')),
        ]),
        ('Pacients', [
            ('Nou pacient', lambda: navigate('alta_pacient')),
            ('Informe pacient', lambda: navigate('report_pacient')),
        ]),
        ('Enfermeria', [
            ('Informe supervisio', lambda: navigate('report_supervisio')),
        ]),
        ('Personal', [
            ('Nou personal', lambda: navigate('alta_personal')),
        ]),
        ('Visites', [
            ('Veure visites', lambda: navigate('report_visites')),
            ('Horari metge', lambda: navigate('report_metge')),
        ]),
        ('Quirofans', [
            ('Veure quirofans', lambda: navigate('report_quirofans')),
            ('Aparells', lambda: navigate('report_aparells')),
        ]),
        ('Habitacions', [
            ('Veure ocupacio', lambda: navigate('report_habitacions')),
        ]),
    ]

    dummy_status_var = tk.StringVar(value='')
    validation_summary_var = tk.StringVar(value='')
    dummy_poll = {'after_id': None}

    row = 1
    admin_title = ttk.Label(card, text='Administracio', style='Section.TLabel')
    admin_title.grid(row=row, column=0, sticky='w', pady=(12, 4))
    row += 1

    def set_admin_buttons_enabled(enabled):
        if enabled:
            admin_generate_button.state(['!disabled'])
            admin_delete_button.state(['!disabled'])
        else:
            admin_generate_button.state(['disabled'])
            admin_delete_button.state(['disabled'])

    def render_dummy_status(status):
        state = (status or {}).get('state') or 'idle'
        action = (status or {}).get('action')
        message = (status or {}).get('message') or 'No hi ha operacions recents.'
        action_text = {
            'generate': 'generacio',
            'delete': 'eliminacio',
        }.get(action, 'dummy data')

        if state == 'running':
            prefix = 'En curs'
            set_admin_buttons_enabled(False)
        elif state == 'success':
            prefix = 'Ultima operacio'
            set_admin_buttons_enabled(True)
        elif state == 'error':
            prefix = 'Error'
            set_admin_buttons_enabled(True)
        else:
            prefix = 'Estat'
            set_admin_buttons_enabled(True)

        dummy_status_var.set(f'{prefix} ({action_text}): {message}')

    def render_validation_preview(validation):
        preserved_user = (validation or {}).get('preserved_user') or {}
        expected_insert_counts = (validation or {}).get('expected_insert_counts') or {}
        source_files = (validation or {}).get('source_files') or []
        table_counts = (validation or {}).get('table_counts') or []
        generate_issues = (validation or {}).get('generate_issues') or []
        delete_issues = (validation or {}).get('delete_issues') or []
        warnings = (validation or {}).get('warnings') or []

        lines = [
            'Validacio previa del dummy data',
            f"Usuari preservat: {preserved_user.get('username', '-')} | id_intern {preserved_user.get('id_intern', '-')} | {preserved_user.get('tipus_feina', '-')} | DNI {preserved_user.get('dni', '-')}",
            f"Preparat per generar: {'SI' if (validation or {}).get('ready_for_generate') else 'NO'}",
            f"Preparat per eliminar: {'SI' if (validation or {}).get('ready_for_delete') else 'NO'}",
            f"Usuaris que s'eliminarien: {(validation or {}).get('users_to_delete', 0)}",
            f"Registres de personal que s'eliminarien: {(validation or {}).get('personal_to_delete', 0)}",
            '',
            'Impacte actual per taula:',
        ]

        for entry in table_counts:
            lines.append(f"- {entry.get('table')}: {entry.get('count')}")

        lines.extend([
            '',
            'Impacte previst en generar:',
        ])

        for table_name, value in expected_insert_counts.items():
            lines.append(f"- {table_name}: +{value}")

        lines.extend([
            '',
            'Fonts de dades dummy:',
        ])

        for source in source_files:
            state = 'OK' if source.get('exists') else 'FALTA'
            lines.append(f"- {source.get('file')}: {state}, elements={source.get('items')}")

        if generate_issues:
            lines.extend(['', 'Bloquejos per generar:'])
            for issue in generate_issues:
                lines.append(f'- {issue}')

        if delete_issues:
            lines.extend(['', 'Bloquejos per eliminar:'])
            for issue in delete_issues:
                lines.append(f'- {issue}')

        if warnings:
            lines.extend(['', 'Avisos:'])
            for warning in warnings:
                lines.append(f'- {warning}')

        validation_summary_var.set('\n'.join(lines))
        frame.after_idle(sync_scroll_region)

    def cancel_dummy_status_poll():
        after_id = dummy_poll.get('after_id')
        if after_id is not None:
            frame.after_cancel(after_id)
            dummy_poll['after_id'] = None

    def can_manage_dummy_data():
        return app_state.get('role') == 'administrador'

    def refresh_dummy_status(reschedule=False):
        dummy_poll['after_id'] = None

        if not can_manage_dummy_data():
            return

        try:
            status = api.get_dummy_data_status()
        except Exception as exc:
            dummy_status_var.set(f'Error consultant l\'estat: {exc}')
            set_admin_buttons_enabled(True)
            return

        render_dummy_status(status)
        if reschedule or status.get('state') == 'running':
            dummy_poll['after_id'] = frame.after(2000, lambda: refresh_dummy_status(True))

    def start_dummy_action(title, prompt_text, api_call):
        if not can_manage_dummy_data():
            messagebox.showerror(title, 'Nomes els administradors poden executar aquesta accio.')
            return

        if not messagebox.askyesno(title, prompt_text):
            return

        try:
            payload = api_call()
        except Exception as exc:
            messagebox.showerror(title, str(exc))
            return

        render_dummy_status(payload.get('status', {}))
        validation_summary_var.set('Operacio iniciada. La validacio previa pot haver quedat obsoleta fins que el proces acabi. Pots tornar a validar quan vulguis.')
        refresh_dummy_status(True)

    def validate_before_execute(show_dialog_on_error=False):
        if not can_manage_dummy_data():
            validation_summary_var.set('Validacio no disponible per a usuaris no administradors.')
            return

        validation_summary_var.set('Validant impacte i coherencia abans d\'executar...')
        frame.after_idle(sync_scroll_region)

        try:
            validation = api.validate_dummy_data()
        except Exception as exc:
            validation_summary_var.set(f'Error fent la validacio previa: {exc}')
            if show_dialog_on_error:
                messagebox.showerror('Validacio dummy data', str(exc))
            return

        render_validation_preview(validation)

    admin_validate_button = ttk.Button(
        card,
        text='Validar abans d\'executar',
        command=lambda: validate_before_execute(True),
        style='Secondary.TButton',
    )
    admin_validate_button.grid(row=row, column=0, sticky='we', pady=4)
    row += 1

    admin_generate_button = ttk.Button(
        card,
        text='Generar dummy data',
        command=lambda: start_dummy_action(
            'Generar dummy data',
            'Aquesta accio eliminara totes les dades actuals excepte el teu usuari administrador i carregara dades dummy noves. Vols continuar?',
            api.generate_dummy_data,
        ),
        style='Primary.TButton',
    )
    admin_generate_button.grid(row=row, column=0, sticky='we', pady=4)
    row += 1

    admin_delete_button = ttk.Button(
        card,
        text='Eliminar dummy data',
        command=lambda: start_dummy_action(
            'Eliminar dummy data',
            'Aquesta accio eliminara totes les dades dummy i conservara nomes el teu usuari administrador. Vols continuar?',
            api.delete_dummy_data,
        ),
        style='Secondary.TButton',
    )
    admin_delete_button.grid(row=row, column=0, sticky='we', pady=4)
    row += 1

    admin_status_label = ttk.Label(card, textvariable=dummy_status_var, style='Muted.TLabel', wraplength=760, justify='left')
    admin_status_label.grid(row=row, column=0, sticky='w', pady=(2, 0))
    row += 1

    validation_summary_label = ttk.Label(
        card,
        textvariable=validation_summary_var,
        style='Muted.TLabel',
        wraplength=760,
        justify='left',
    )
    validation_summary_label.grid(row=row, column=0, sticky='w', pady=(8, 0))
    row += 1

    admin_widgets = (
        admin_title,
        admin_validate_button,
        admin_generate_button,
        admin_delete_button,
        admin_status_label,
        validation_summary_label,
    )
    for widget in admin_widgets:
        widget.grid_remove()

    for section_title, section_actions in sections:
        ttk.Label(card, text=section_title, style='Section.TLabel').grid(row=row, column=0, sticky='w', pady=(12, 4))
        row += 1
        for label, command in section_actions:
            ttk.Button(card, text=label, command=command, style='Primary.TButton').grid(row=row, column=0, sticky='we', pady=4)
            row += 1

    ttk.Separator(card, orient='horizontal').grid(row=row, column=0, sticky='we', pady=(12, 8))
    row += 1

    def logout():
        cancel_dummy_status_poll()
        try:
            api.logout()
        except Exception:
            pass
        app_state['username'] = None
        app_state['role'] = None
        navigate('login')

    ttk.Button(card, text='Tancar sessio', command=logout, style='Secondary.TButton').grid(row=row, column=0, sticky='we')

    def on_show():
        username = app_state.get('username') or '-'
        role = app_state.get('role') or 'sense rol'
        user_label.configure(text=f'Hola, {username} ({role})')

        cancel_dummy_status_poll()
        if can_manage_dummy_data():
            for widget in admin_widgets:
                widget.grid()
            dummy_status_var.set('Consultant estat del dummy data...')
            refresh_dummy_status()
            validate_before_execute(False)
        else:
            for widget in admin_widgets:
                widget.grid_remove()
            dummy_status_var.set('')
            validation_summary_var.set('')
            set_admin_buttons_enabled(True)

        frame.after_idle(sync_scroll_region)

    return frame, on_show
