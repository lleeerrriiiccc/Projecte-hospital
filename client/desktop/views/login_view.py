import tkinter as tk
from tkinter import messagebox, ttk

from .. import api_client as api
from ..theme import PALETTE


def create_login_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    shell = ttk.Frame(frame, style='App.TFrame', padding=(40, 32))
    shell.grid(row=0, column=0, sticky='nsew')
    shell.columnconfigure(0, weight=3)
    shell.columnconfigure(1, weight=2)
    shell.rowconfigure(0, weight=1)

    hero = ttk.Frame(shell, style='Hero.TFrame', padding=(34, 34))
    hero.grid(row=0, column=0, sticky='nsew', padx=(0, 18))
    hero.columnconfigure(0, weight=1)

    ttk.Label(hero, text='Hospital Control Center', style='HeroTitle.TLabel').grid(row=0, column=0, sticky='w')
    ttk.Label(
        hero,
        text='Un punt d\'entrada clar per consultar informes, donar d\'alta pacients i gestionar el dia a dia del centre.',
        style='HeroBody.TLabel',
        wraplength=500,
        justify='left',
    ).grid(row=1, column=0, sticky='w', pady=(10, 18))
    ttk.Label(hero, text='Que hi trobaras', style='HeroCaption.TLabel').grid(row=2, column=0, sticky='w', pady=(0, 10))

    features = (
        'Informes i consultes en pocs clics.',
        'Alta rapida de pacients i personal.',
        'Gestio de dummy data només per a administradors.',
    )
    for index, feature in enumerate(features, start=3):
        ttk.Label(hero, text=f'- {feature}', style='HeroList.TLabel', wraplength=500, justify='left').grid(row=index, column=0, sticky='w', pady=2)

    ttk.Label(hero, text='Projecte de gestio hospitalaria per a ASIX', style='HeroCaption.TLabel').grid(row=6, column=0, sticky='w', pady=(22, 0))

    card = ttk.Frame(shell, style='Card.TFrame', padding=30)
    card.grid(row=0, column=1, sticky='nsew')
    card.columnconfigure(0, weight=1)

    ttk.Label(card, text='Inicia sessio', style='Title.TLabel').grid(row=0, column=0, sticky='w')
    ttk.Label(card, text="Accedeix amb el teu usuari per entrar al panell intern.", style='Subtitle.TLabel').grid(row=1, column=0, sticky='w', pady=(6, 18))

    message_var = tk.StringVar(value='')
    message_label = ttk.Label(card, textvariable=message_var, style='Error.TLabel', wraplength=340, justify='left')
    message_label.grid(row=2, column=0, sticky='we', pady=(0, 10))
    message_label.grid_remove()

    form = ttk.Frame(card)
    form.grid(row=3, column=0, sticky='we')
    form.columnconfigure(0, weight=1)

    ttk.Label(form, text='Usuari').grid(row=0, column=0, sticky='w')
    username_entry = ttk.Entry(form, width=32)
    username_entry.grid(row=1, column=0, sticky='we', pady=(4, 12))

    ttk.Label(form, text='Contrasenya').grid(row=2, column=0, sticky='w')
    password_entry = ttk.Entry(form, width=32, show='*')
    password_entry.grid(row=3, column=0, sticky='we', pady=(4, 8))

    show_password = tk.BooleanVar(value=False)

    def toggle_password():
        password_entry.configure(show='' if show_password.get() else '*')

    ttk.Checkbutton(
        form,
        text='Mostrar contrasenya',
        variable=show_password,
        command=toggle_password,
        style='Inline.TCheckbutton',
    ).grid(row=4, column=0, sticky='w', pady=(0, 14))

    def show_error(text):
        message_var.set(text)
        message_label.grid()

    def clear_error():
        message_var.set('')
        message_label.grid_remove()

    def handle_login():
        username = username_entry.get().strip()
        password = password_entry.get()

        if not username or not password:
            show_error('Completa usuari i contrasenya.')
            return

        clear_error()

        try:
            payload = api.login(username, password)
            app_state['username'] = payload.get('username')
            app_state['role'] = payload.get('role')
            navigate('home')
        except Exception as exc:
            show_error(str(exc))

    def open_register_dialog():
        dialog = tk.Toplevel(frame)
        dialog.title('Registrar usuari')
        dialog.configure(bg=PALETTE['bg'])
        dialog.transient(frame.winfo_toplevel())
        dialog.grab_set()
        dialog.resizable(False, False)

        d_frame = ttk.Frame(dialog, style='Card.TFrame', padding=18)
        d_frame.grid(row=0, column=0, padx=14, pady=14)
        d_frame.columnconfigure(0, weight=1)

        ttk.Label(d_frame, text='Crear compte', style='Title.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 8))
        ttk.Label(d_frame, text='Registra un usuari nou amb el seu id intern.', style='Subtitle.TLabel').grid(row=1, column=0, sticky='w', pady=(0, 14))

        ttk.Label(d_frame, text='Usuari').grid(row=2, column=0, sticky='w')
        reg_username = ttk.Entry(d_frame, width=28)
        reg_username.grid(row=3, column=0, sticky='we', pady=(4, 8))

        ttk.Label(d_frame, text='Contrasenya').grid(row=4, column=0, sticky='w')
        reg_password = ttk.Entry(d_frame, width=28, show='*')
        reg_password.grid(row=5, column=0, sticky='we', pady=(4, 8))

        ttk.Label(d_frame, text='Repeteix contrasenya').grid(row=6, column=0, sticky='w')
        reg_confirm = ttk.Entry(d_frame, width=28, show='*')
        reg_confirm.grid(row=7, column=0, sticky='we', pady=(4, 8))

        ttk.Label(d_frame, text='ID intern').grid(row=8, column=0, sticky='w')
        reg_id = ttk.Entry(d_frame, width=28)
        reg_id.grid(row=9, column=0, sticky='we', pady=(4, 8))

        reg_message = tk.StringVar(value='')
        reg_message_lbl = ttk.Label(d_frame, textvariable=reg_message, style='Error.TLabel', wraplength=280, justify='left')
        reg_message_lbl.grid(row=10, column=0, sticky='we')
        reg_message_lbl.grid_remove()

        def submit_register():
            username = reg_username.get().strip()
            password = reg_password.get()
            confirm = reg_confirm.get()
            id_intern_raw = reg_id.get().strip()

            if not id_intern_raw.isdigit():
                reg_message.set('ID intern ha de ser numeric.')
                reg_message_lbl.grid()
                return

            try:
                api.register(username, password, confirm, int(id_intern_raw))
                dialog.destroy()
                messagebox.showinfo('Registro', 'Cuenta creada correctamente')
            except Exception as exc:
                reg_message.set(str(exc))
                reg_message_lbl.grid()

        ttk.Button(d_frame, text='Crear compte', style='Primary.TButton', command=submit_register).grid(row=11, column=0, sticky='we', pady=(8, 0))
        dialog.bind('<Return>', lambda _event: submit_register())

        reg_username.focus_set()

    ttk.Button(form, text='Entrar', command=handle_login, style='Primary.TButton').grid(row=5, column=0, sticky='we')
    ttk.Button(form, text='Crear compte', command=open_register_dialog, style='Secondary.TButton').grid(row=6, column=0, sticky='we', pady=(8, 0))

    form.bind('<Return>', lambda _event: handle_login())
    username_entry.bind('<Return>', lambda _event: handle_login())
    password_entry.bind('<Return>', lambda _event: handle_login())

    username_entry.focus_set()

    def on_show():
        password_entry.delete(0, tk.END)
        show_password.set(False)
        toggle_password()
        clear_error()
        username_entry.focus_set()

    return frame, on_show
