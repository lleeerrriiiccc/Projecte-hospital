import datetime
import tkinter as tk
from tkinter import filedialog, ttk

from .. import api_client as api
from .base import today_iso, parse_iso_date, build_options_map, build_combo_values, split_combo_value


WORK_TYPES = [
    'metge',
    'infermer',
    'administratiu',
    'tecnic',
    'personal neteja',
    'personal seguretat',
    'personal cuina',
]


def create_alta_personal_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    card = ttk.Frame(frame, style='Card.TFrame', padding=20)
    card.grid(row=0, column=0, sticky='nsew', padx=16, pady=16)
    card.columnconfigure(1, weight=1)

    ttk.Label(card, text='Alta de Personal', style='Title.TLabel').grid(row=0, column=0, columnspan=2, sticky='w')
    ttk.Label(card, text='Introduce los datos obligatorios del personal.', style='Muted.TLabel').grid(row=1, column=0, columnspan=2, sticky='w', pady=(5, 8))

    status_var = tk.StringVar(value='')
    ttk.Label(card, textvariable=status_var, style='Muted.TLabel').grid(row=2, column=0, columnspan=2, sticky='we')

    # Camps principals
    ttk.Label(card, text='Nom').grid(row=3, column=0, sticky='w', pady=3)
    nom_entry = ttk.Entry(card, width=42)
    nom_entry.grid(row=3, column=1, sticky='we', pady=3)

    ttk.Label(card, text='Primer cognom').grid(row=4, column=0, sticky='w', pady=3)
    cognom_entry = ttk.Entry(card, width=42)
    cognom_entry.grid(row=4, column=1, sticky='we', pady=3)

    ttk.Label(card, text='Segon cognom').grid(row=5, column=0, sticky='w', pady=3)
    cognom2_entry = ttk.Entry(card, width=42)
    cognom2_entry.grid(row=5, column=1, sticky='we', pady=3)

    ttk.Label(card, text='Data naixement (YYYY-MM-DD)').grid(row=6, column=0, sticky='w', pady=3)
    data_naix_entry = ttk.Entry(card, width=42)
    data_naix_entry.grid(row=6, column=1, sticky='we', pady=3)

    ttk.Label(card, text='Telefon principal').grid(row=7, column=0, sticky='w', pady=3)
    telefon_entry = ttk.Entry(card, width=42)
    telefon_entry.grid(row=7, column=1, sticky='we', pady=3)

    ttk.Label(card, text='Telefon secundari').grid(row=8, column=0, sticky='w', pady=3)
    telefon2_entry = ttk.Entry(card, width=42)
    telefon2_entry.grid(row=8, column=1, sticky='we', pady=3)

    ttk.Label(card, text='Email personal').grid(row=9, column=0, sticky='w', pady=3)
    email_entry = ttk.Entry(card, width=42)
    email_entry.grid(row=9, column=1, sticky='we', pady=3)

    ttk.Label(card, text='Email intern').grid(row=10, column=0, sticky='w', pady=3)
    email_intern_entry = ttk.Entry(card, width=42)
    email_intern_entry.grid(row=10, column=1, sticky='we', pady=3)

    ttk.Label(card, text='DNI').grid(row=11, column=0, sticky='w', pady=3)
    dni_entry = ttk.Entry(card, width=42)
    dni_entry.grid(row=11, column=1, sticky='we', pady=3)

    ttk.Label(card, text='Data alta (YYYY-MM-DD)').grid(row=12, column=0, sticky='w', pady=3)
    data_alta_entry = ttk.Entry(card, width=42)
    data_alta_entry.grid(row=12, column=1, sticky='we', pady=3)
    data_alta_entry.insert(0, today_iso())

    ttk.Label(card, text='Tipus feina').grid(row=13, column=0, sticky='w', pady=3)
    tipus_combo = ttk.Combobox(card, values=WORK_TYPES, state='readonly')
    tipus_combo.grid(row=13, column=1, sticky='we', pady=3)

    # Frame per als camps dinàmics (metge/infermer)
    dynamic_frame = ttk.Frame(card)
    dynamic_frame.grid(row=14, column=0, columnspan=2, sticky='we', pady=(4, 0))
    dynamic_frame.columnconfigure(1, weight=1)

    buttons = ttk.Frame(card)
    buttons.grid(row=15, column=0, columnspan=2, sticky='we', pady=(12, 0))
    buttons.columnconfigure(0, weight=1)
    buttons.columnconfigure(1, weight=1)

    # Variables per als camps dinàmics
    metges_map = {}
    cap_de_planta_var = tk.BooleanVar(value=False)
    cv_path_var = tk.StringVar(value='')
    dynamic_widgets = {}  # Emmagatzema widgets dinàmics actuals

    def load_metges():
        if metges_map:
            return
        payload = api.get_metges()
        rows = payload.get('data') or []
        loaded = build_options_map(rows, ['id_intern', 'id'], ['nom_complet', 'nom'])
        metges_map.update(loaded)

    def toggle_supervisor():
        combo = dynamic_widgets.get('supervisor_combo')
        if combo is None:
            return
        if cap_de_planta_var.get():
            combo.configure(state='disabled')
            combo.set('')
        else:
            combo.configure(state='readonly')

    def browse_cv():
        file_path = filedialog.askopenfilename(
            title='Selecciona el CV',
            filetypes=[('Documents', '*.pdf *.doc *.docx'), ('All files', '*.*')],
        )
        if file_path:
            cv_path_var.set(file_path)

    def render_dynamic_fields():
        for child in dynamic_frame.winfo_children():
            child.destroy()
        dynamic_widgets.clear()

        selected = tipus_combo.get().strip()

        if selected == 'metge':
            ttk.Label(dynamic_frame, text='Especialitat').grid(row=0, column=0, sticky='w', pady=3)
            especialitat_entry = ttk.Entry(dynamic_frame)
            especialitat_entry.grid(row=0, column=1, sticky='we', pady=3)
            dynamic_widgets['especialitat_entry'] = especialitat_entry

            ttk.Label(dynamic_frame, text='CV').grid(row=1, column=0, sticky='w', pady=3)
            cv_frame = ttk.Frame(dynamic_frame)
            cv_frame.grid(row=1, column=1, sticky='we', pady=3)
            cv_frame.columnconfigure(0, weight=1)
            ttk.Entry(cv_frame, textvariable=cv_path_var).grid(row=0, column=0, sticky='we')
            ttk.Button(cv_frame, text='Seleccionar', command=browse_cv).grid(row=0, column=1, padx=(6, 0))

        elif selected == 'infermer':
            try:
                load_metges()
            except Exception as exc:
                status_var.set(f'No se pudieron cargar metges: {exc}')
                return

            ttk.Checkbutton(
                dynamic_frame, text='Cap de planta',
                variable=cap_de_planta_var, command=toggle_supervisor,
            ).grid(row=0, column=0, columnspan=2, sticky='w', pady=3)

            ttk.Label(dynamic_frame, text='Metge supervisor').grid(row=1, column=0, sticky='w', pady=3)
            values = build_combo_values(metges_map)
            supervisor_combo = ttk.Combobox(dynamic_frame, values=values, state='readonly')
            supervisor_combo.grid(row=1, column=1, sticky='we', pady=3)
            dynamic_widgets['supervisor_combo'] = supervisor_combo
            toggle_supervisor()

    tipus_combo.bind('<<ComboboxSelected>>', lambda _evt: render_dynamic_fields())

    def reset_form():
        for entry in [nom_entry, cognom_entry, cognom2_entry, data_naix_entry,
                      telefon_entry, telefon2_entry, email_entry, email_intern_entry,
                      dni_entry]:
            entry.delete(0, tk.END)
        data_alta_entry.delete(0, tk.END)
        data_alta_entry.insert(0, today_iso())
        tipus_combo.set('')
        cv_path_var.set('')
        cap_de_planta_var.set(False)
        render_dynamic_fields()

    def submit():
        nom = nom_entry.get().strip()
        cognom = cognom_entry.get().strip()
        cognom2 = cognom2_entry.get().strip()
        data_naix = data_naix_entry.get().strip()
        telefon = telefon_entry.get().strip()
        telefon2 = telefon2_entry.get().strip()
        email = email_entry.get().strip()
        email_intern = email_intern_entry.get().strip()
        dni = dni_entry.get().strip().upper()
        tipus_feina = tipus_combo.get().strip()
        data_alta = data_alta_entry.get().strip()

        if not nom or not cognom or not cognom2 or not data_naix or not telefon or not email or not email_intern or not dni or not tipus_feina or not data_alta:
            status_var.set('Completa todos los campos obligatorios.')
            return

        try:
            birth_date = parse_iso_date(data_naix, 'Data naixement invalida. Usa YYYY-MM-DD.')
        except ValueError as exc:
            status_var.set(str(exc))
            return

        if birth_date > datetime.date.today():
            status_var.set('La data de naixement no pot ser futura.')
            return

        try:
            parse_iso_date(data_alta, 'Data alta invalida. Usa YYYY-MM-DD.')
        except ValueError as exc:
            status_var.set(str(exc))
            return

        payload = {
            'nom': nom, 'cognom': cognom, 'cognom2': cognom2,
            'data_naixement': data_naix, 'telefon': telefon, 'telefon2': telefon2,
            'email': email, 'email_intern': email_intern, 'dni': dni,
            'tipus_feina': tipus_feina, 'data_alta': data_alta,
        }

        if tipus_feina == 'metge':
            especialitat_entry = dynamic_widgets.get('especialitat_entry')
            if not especialitat_entry or not especialitat_entry.get().strip():
                status_var.set('Especialitat es obligatoria para metge.')
                return
            if not cv_path_var.get().strip():
                status_var.set('CV es obligatorio para metge.')
                return
            payload['especialitat'] = especialitat_entry.get().strip()
            payload['cv_path'] = cv_path_var.get().strip()

        if tipus_feina == 'infermer':
            payload['cap_de_planta'] = bool(cap_de_planta_var.get())
            if not payload['cap_de_planta']:
                supervisor_combo = dynamic_widgets.get('supervisor_combo')
                selected_value = supervisor_combo.get().strip() if supervisor_combo else ''
                if not selected_value:
                    status_var.set('Selecciona un metge supervisor o marca cap de planta.')
                    return
                payload['id_metge_supervisor'] = split_combo_value(selected_value)

        try:
            api.create_personal(payload)
            status_var.set('Personal dado de alta correctamente.')
            reset_form()
        except Exception as exc:
            status_var.set(str(exc))

    ttk.Button(buttons, text='Guardar', style='Primary.TButton', command=submit).grid(row=0, column=0, sticky='we', padx=(0, 6))
    ttk.Button(buttons, text='Volver', command=lambda: navigate('home')).grid(row=0, column=1, sticky='we', padx=(6, 0))

    render_dynamic_fields()

    def on_show():
        status_var.set('')

    return frame, on_show
