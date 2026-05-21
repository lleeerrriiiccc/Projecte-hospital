import tkinter as tk
from tkinter import messagebox, ttk

from .. import api_client as api
from ..theme import PALETTE


def create_home_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(1, weight=1)

    dummy_status_var = tk.StringVar(value='Sense operacions recents.')
    dummy_state_var = tk.StringVar(value='Preparat')
    validation_summary_var = tk.StringVar(value='Fes una validacio previa per veure l\'impacte abans d\'executar res.')
    validation_details_var = tk.StringVar(value='')
    validation_toggle_var = tk.StringVar(value='Mostrar detall')
    dummy_poll = {'after_id': None}
    validation_panel = {'expanded': False}

    def logout():
        cancel_dummy_status_poll()
        try:
            api.logout()
        except Exception:
            pass
        app_state['username'] = None
        app_state['role'] = None
        navigate('login')

    topbar = ttk.Frame(frame, style='Topbar.TFrame', padding=(18, 12))
    topbar.grid(row=0, column=0, sticky='we')
    topbar.columnconfigure(0, weight=1)

    ttk.Label(topbar, text='Gestio Hospitalaria', style='TopbarTitle.TLabel').grid(row=0, column=0, sticky='w')

    topbar_actions = ttk.Frame(topbar, style='Topbar.TFrame')
    topbar_actions.grid(row=0, column=1, sticky='e')
    user_label = ttk.Label(topbar_actions, text='', style='TopbarMuted.TLabel')
    user_label.grid(row=0, column=0, sticky='e', padx=(0, 12))
    ttk.Button(topbar_actions, text='Tancar sessio', style='Topbar.TButton', command=logout).grid(row=0, column=1, sticky='e')

    main = ttk.Frame(frame, style='App.TFrame')
    main.grid(row=1, column=0, sticky='nsew')
    main.columnconfigure(0, weight=1)
    main.rowconfigure(0, weight=1)

    canvas = tk.Canvas(main, background=PALETTE['bg'], borderwidth=0, highlightthickness=0)
    canvas.grid(row=0, column=0, sticky='nsew', padx=(16, 0), pady=16)

    scrollbar = ttk.Scrollbar(main, orient='vertical', command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky='ns', padx=(8, 16), pady=16)

    canvas.configure(yscrollcommand=scrollbar.set)

    content = ttk.Frame(canvas, style='App.TFrame')
    content.columnconfigure(0, weight=1)
    content.columnconfigure(1, weight=1)
    content_window = canvas.create_window((0, 0), window=content, anchor='nw')

    def sync_scroll_region(_event=None):
        canvas.configure(scrollregion=canvas.bbox('all'))

    def sync_card_width(event):
        canvas.itemconfigure(content_window, width=max(event.width - 4, 100))

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def bind_mousewheel(_event):
        canvas.bind_all('<MouseWheel>', on_mousewheel)

    def unbind_mousewheel(_event):
        canvas.unbind_all('<MouseWheel>')

    content.bind('<Configure>', sync_scroll_region)
    canvas.bind('<Configure>', sync_card_width)
    canvas.bind('<Enter>', bind_mousewheel)
    canvas.bind('<Leave>', unbind_mousewheel)

    hero_card = ttk.Frame(content, style='Card.TFrame', padding=(22, 20))
    hero_card.grid(row=0, column=0, columnspan=2, sticky='we', pady=(0, 16))
    hero_card.columnconfigure(0, weight=1)

    ttk.Label(hero_card, text='Panell principal', style='Title.TLabel').grid(row=0, column=0, sticky='w')
    ttk.Label(
        hero_card,
        text='Accedeix rapidament a cada area del projecte des d\'un panell mes clar i facil de navegar.',
        style='Subtitle.TLabel',
        wraplength=900,
        justify='left',
    ).grid(row=1, column=0, sticky='w', pady=(6, 14))

    hero_meta = ttk.Frame(hero_card, style='Card.TFrame')
    hero_meta.grid(row=2, column=0, sticky='w')
    ttk.Label(hero_meta, text='Panell intern', style='Badge.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 8))
    role_badge = ttk.Label(hero_meta, text='', style='Badge.TLabel')
    role_badge.grid(row=0, column=1, sticky='w', padx=(0, 8))
    section_badge = ttk.Label(hero_meta, text='7 arees principals', style='Badge.TLabel')
    section_badge.grid(row=0, column=2, sticky='w')

    # Seccions de navegació agrupades per àrea
    sections = [
        ('Consultes i informes', 'Informes generals, ranking i estadistiques del centre.', [
            ('Informe per planta', lambda: navigate('report_planta')),
            ('Informe personal', lambda: navigate('report_personal')),
            ('Malalties més comunes', lambda: navigate('report_malalties')),
            ('Ranking de metges', lambda: navigate('report_ranking_metges')),
            ('Visites per dia', lambda: navigate('report_visites_dia')),
        ]),
        ('Pacients', 'Alta de nous pacients i consulta d\'informacio clínica.', [
            ('Nou pacient', lambda: navigate('alta_pacient')),
            ('Informe pacient', lambda: navigate('report_pacient')),
        ]),
        ('Enfermeria', 'Consulta la supervisio i el seguiment dels equips.', [
            ('Informe supervisio', lambda: navigate('report_supervisio')),
        ]),
        ('Personal', 'Gestio del personal del centre i nous registres.', [
            ('Nou personal', lambda: navigate('alta_personal')),
        ]),
        ('Visites', 'Accedeix al llistat de visites i a l\'horari del metge.', [
            ('Veure visites', lambda: navigate('report_visites')),
            ('Horari metge', lambda: navigate('report_metge')),
        ]),
        ('Quirofans', 'Consulta espais quirurgics i l\'inventari d\'aparells.', [
            ('Veure quirofans', lambda: navigate('report_quirofans')),
            ('Aparells', lambda: navigate('report_aparells')),
        ]),
        ('Habitacions', 'Revisa l\'ocupacio i l\'estat general de les habitacions.', [
            ('Veure ocupacio', lambda: navigate('report_habitacions')),
        ]),
    ]

    admin_card = ttk.Frame(content, style='AltCard.TFrame', padding=(22, 18))
    admin_card.grid(row=1, column=0, columnspan=2, sticky='we', pady=(0, 16))
    admin_card.columnconfigure(0, weight=1)

    admin_header = ttk.Frame(admin_card, style='AltCard.TFrame')
    admin_header.grid(row=0, column=0, sticky='we')
    admin_header.columnconfigure(0, weight=1)

    ttk.Label(admin_header, text='Administracio i dummy data', style='AltTitle.TLabel').grid(row=0, column=0, sticky='w')
    ttk.Label(admin_header, textvariable=dummy_state_var, style='Badge.TLabel').grid(row=0, column=1, sticky='e')
    ttk.Label(
        admin_card,
        text='Valida l\'impacte abans d\'executar accions destructives. Els botons es desactiven mentre hi ha una operacio en curs.',
        style='AltBody.TLabel',
        wraplength=920,
        justify='left',
    ).grid(row=1, column=0, sticky='w', pady=(6, 14))

    def set_admin_buttons_enabled(enabled):
        if enabled:
            admin_generate_button.state(['!disabled'])
            admin_delete_button.state(['!disabled'])
            admin_validate_button.state(['!disabled'])
        else:
            admin_generate_button.state(['disabled'])
            admin_delete_button.state(['disabled'])
            admin_validate_button.state(['disabled'])

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
            dummy_state_var.set('En curs')
            set_admin_buttons_enabled(False)
        elif state == 'success':
            prefix = 'Ultima operacio'
            dummy_state_var.set('Correcte')
            set_admin_buttons_enabled(True)
        elif state == 'error':
            prefix = 'Error'
            dummy_state_var.set('Revisar')
            set_admin_buttons_enabled(True)
        else:
            prefix = 'Estat'
            dummy_state_var.set('Preparat')
            set_admin_buttons_enabled(True)

        dummy_status_var.set(f'{prefix} ({action_text}): {message}')

    def set_validation_details_enabled(enabled):
        if enabled:
            validation_toggle_button.state(['!disabled'])
        else:
            validation_toggle_button.state(['disabled'])

    def set_validation_expanded(expanded):
        has_details = bool(validation_details_var.get())
        validation_panel['expanded'] = expanded and has_details

        if validation_panel['expanded']:
            validation_toggle_var.set('Ocultar detall')
            validation_details_label.grid()
        else:
            validation_toggle_var.set('Mostrar detall')
            validation_details_label.grid_remove()

        set_validation_details_enabled(has_details)
        frame.after_idle(sync_scroll_region)

    def update_validation_panel(summary_text, details_text=''):
        validation_summary_var.set(summary_text)
        validation_details_var.set(details_text)
        set_validation_expanded(False)

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

        summary_lines = [
            f"Usuari preservat: {preserved_user.get('username', '-')} ({preserved_user.get('tipus_feina', '-')})",
            f"Preparat per generar: {'SI' if (validation or {}).get('ready_for_generate') else 'NO'} | Preparat per eliminar: {'SI' if (validation or {}).get('ready_for_delete') else 'NO'}",
            f"Usuaris a eliminar: {(validation or {}).get('users_to_delete', 0)} | Personal a eliminar: {(validation or {}).get('personal_to_delete', 0)}",
        ]

        if generate_issues or delete_issues or warnings:
            summary_lines.append(
                f'Bloquejos generar: {len(generate_issues)} | Bloquejos eliminar: {len(delete_issues)} | Avisos: {len(warnings)}'
            )
        else:
            summary_lines.append('No s\'han detectat bloquejos ni avisos.')

        update_validation_panel('\n'.join(summary_lines), '\n'.join(lines))

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
        update_validation_panel(
            'Operacio iniciada. La validacio previa pot haver quedat obsoleta fins que el proces acabi.\nPots tornar a validar quan vulguis.'
        )
        refresh_dummy_status(True)

    def validate_before_execute(show_dialog_on_error=False):
        if not can_manage_dummy_data():
            update_validation_panel('Validacio no disponible per a usuaris no administradors.')
            return

        update_validation_panel('Validant impacte i coherencia abans d\'executar...')

        try:
            validation = api.validate_dummy_data()
        except Exception as exc:
            update_validation_panel(f'Error fent la validacio previa: {exc}')
            if show_dialog_on_error:
                messagebox.showerror('Validacio dummy data', str(exc))
            return

        render_validation_preview(validation)

    admin_actions = ttk.Frame(admin_card, style='AltCard.TFrame')
    admin_actions.grid(row=2, column=0, sticky='we')
    admin_actions.columnconfigure(0, weight=1)
    admin_actions.columnconfigure(1, weight=1)
    admin_actions.columnconfigure(2, weight=1)

    admin_validate_button = ttk.Button(
        admin_actions,
        text='Validar abans d\'executar',
        command=lambda: validate_before_execute(True),
        style='Secondary.TButton',
    )
    admin_validate_button.grid(row=0, column=0, sticky='we', padx=(0, 6))

    admin_generate_button = ttk.Button(
        admin_actions,
        text='Generar dummy data',
        command=lambda: start_dummy_action(
            'Generar dummy data',
            'Aquesta accio eliminara totes les dades actuals excepte el teu usuari administrador i carregara dades dummy noves. Vols continuar?',
            api.generate_dummy_data,
        ),
        style='Primary.TButton',
    )
    admin_generate_button.grid(row=0, column=1, sticky='we', padx=6)

    admin_delete_button = ttk.Button(
        admin_actions,
        text='Eliminar dummy data',
        command=lambda: start_dummy_action(
            'Eliminar dummy data',
            'Aquesta accio eliminara totes les dades dummy i conservara nomes el teu usuari administrador. Vols continuar?',
            api.delete_dummy_data,
        ),
        style='Danger.TButton',
    )
    admin_delete_button.grid(row=0, column=2, sticky='we', padx=(6, 0))

    admin_status_label = ttk.Label(admin_card, textvariable=dummy_status_var, style='Status.TLabel', wraplength=920, justify='left')
    admin_status_label.grid(row=3, column=0, sticky='we', pady=(12, 10))

    validation_box = ttk.Frame(admin_card, style='Card.TFrame', padding=(14, 12))
    validation_box.grid(row=4, column=0, sticky='we')
    validation_box.columnconfigure(0, weight=1)
    validation_header = ttk.Frame(validation_box, style='Card.TFrame')
    validation_header.grid(row=0, column=0, sticky='we')
    validation_header.columnconfigure(0, weight=1)
    ttk.Label(validation_header, text='Resum de validacio', style='CardTitle.TLabel').grid(row=0, column=0, sticky='w')
    validation_toggle_button = ttk.Button(
        validation_header,
        textvariable=validation_toggle_var,
        command=lambda: set_validation_expanded(not validation_panel['expanded']),
        style='Secondary.TButton',
    )
    validation_toggle_button.grid(row=0, column=1, sticky='e')
    validation_summary_label = ttk.Label(
        validation_box,
        textvariable=validation_summary_var,
        style='CardBody.TLabel',
        wraplength=920,
        justify='left',
    )
    validation_summary_label.grid(row=1, column=0, sticky='w', pady=(10, 0))
    validation_details_label = ttk.Label(
        validation_box,
        textvariable=validation_details_var,
        style='CardBody.TLabel',
        wraplength=920,
        justify='left',
    )
    validation_details_label.grid(row=2, column=0, sticky='w', pady=(10, 0))
    validation_details_label.grid_remove()
    set_validation_details_enabled(False)

    def build_section_card(parent_frame, grid_row, grid_column, title, description, actions):
        pad_left = 0 if grid_column == 0 else 8
        pad_right = 8 if grid_column == 0 else 0
        section_card = ttk.Frame(parent_frame, style='Card.TFrame', padding=(18, 16))
        section_card.grid(row=grid_row, column=grid_column, sticky='nsew', padx=(pad_left, pad_right), pady=(0, 16))
        section_card.columnconfigure(0, weight=1)

        ttk.Label(section_card, text=title, style='CardTitle.TLabel').grid(row=0, column=0, sticky='w')
        ttk.Label(section_card, text=description, style='CardBody.TLabel', wraplength=420, justify='left').grid(row=1, column=0, sticky='w', pady=(6, 12))

        for action_index, (label, command) in enumerate(actions, start=2):
            button_style = 'Primary.TButton' if action_index == 2 else 'Secondary.TButton'
            ttk.Button(section_card, text=label, command=command, style=button_style).grid(row=action_index, column=0, sticky='we', pady=4)

    section_start_row = 2
    for index, (section_title, section_description, section_actions) in enumerate(sections):
        build_section_card(content, section_start_row + (index // 2), index % 2, section_title, section_description, section_actions)

    def on_show():
        username = app_state.get('username') or '-'
        role = app_state.get('role') or 'sense rol'
        user_label.configure(text=f'Hola, {username} ({role})')
        role_badge.configure(text=f'Rol: {role}')
        canvas.yview_moveto(0)

        cancel_dummy_status_poll()
        if can_manage_dummy_data():
            admin_card.grid()
            dummy_status_var.set('Consultant estat del dummy data...')
            refresh_dummy_status()
            validate_before_execute(False)
        else:
            admin_card.grid_remove()
            dummy_status_var.set('Sense operacions recents.')
            dummy_state_var.set('Preparat')
            update_validation_panel('La validacio del dummy data només esta disponible per a administradors.')
            set_admin_buttons_enabled(True)

        frame.after_idle(sync_scroll_region)

    return frame, on_show
