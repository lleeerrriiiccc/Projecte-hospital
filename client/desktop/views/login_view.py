import tkinter as tk
from tkinter import messagebox, ttk

from .. import api_client as api
from ..theme import PALETTE


def create_login_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    card = ttk.Frame(frame, style='Card.TFrame', padding=30)
    card.grid(row=0, column=0, padx=16, pady=24)

    ttk.Label(card, text='Hospital Control Center', style='Title.TLabel').grid(row=0, column=0, sticky='w')
    ttk.Label(card, text="Autentica't per accedir a l'entorn hospitalari.", style='Muted.TLabel').grid(row=1, column=0, sticky='w', pady=(6, 16))

    message_var = tk.StringVar(value='')
    message_label = ttk.Label(card, textvariable=message_var, style='Error.TLabel')
    message_label.grid(row=2, column=0, sticky='we', pady=(0, 10))
    message_label.grid_remove()

    form = ttk.Frame(card)
    form.grid(row=3, column=0, sticky='we')

    ttk.Label(form, text='Usuario').grid(row=0, column=0, sticky='w')
    username_entry = ttk.Entry(form, width=32)
    username_entry.grid(row=1, column=0, sticky='we', pady=(4, 10))

    ttk.Label(form, text='Contrasena').grid(row=2, column=0, sticky='w')
    password_entry = ttk.Entry(form, width=32, show='*')
    password_entry.grid(row=3, column=0, sticky='we', pady=(4, 14))

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
            show_error('Completa usuario y contrasena.')
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

        d_frame = ttk.Frame(dialog, style='Card.TFrame', padding=18)
        d_frame.grid(row=0, column=0, padx=14, pady=14)

        ttk.Label(d_frame, text='Crear compte', style='Title.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 8))

        ttk.Label(d_frame, text='Usuario').grid(row=1, column=0, sticky='w')
        reg_username = ttk.Entry(d_frame, width=28)
        reg_username.grid(row=2, column=0, sticky='we', pady=(4, 8))

        ttk.Label(d_frame, text='Contrasena').grid(row=3, column=0, sticky='w')
        reg_password = ttk.Entry(d_frame, width=28, show='*')
        reg_password.grid(row=4, column=0, sticky='we', pady=(4, 8))

        ttk.Label(d_frame, text='Repite contrasena').grid(row=5, column=0, sticky='w')
        reg_confirm = ttk.Entry(d_frame, width=28, show='*')
        reg_confirm.grid(row=6, column=0, sticky='we', pady=(4, 8))

        ttk.Label(d_frame, text='ID intern').grid(row=7, column=0, sticky='w')
        reg_id = ttk.Entry(d_frame, width=28)
        reg_id.grid(row=8, column=0, sticky='we', pady=(4, 8))

        reg_message = tk.StringVar(value='')
        reg_message_lbl = ttk.Label(d_frame, textvariable=reg_message, style='Error.TLabel')
        reg_message_lbl.grid(row=9, column=0, sticky='we')
        reg_message_lbl.grid_remove()

        def submit_register():
            username = reg_username.get().strip()
            password = reg_password.get()
            confirm = reg_confirm.get()
            id_intern_raw = reg_id.get().strip()

            if not id_intern_raw.isdigit():
                reg_message.set('ID intern debe ser numerico')
                reg_message_lbl.grid()
                return

            try:
                api.register(username, password, confirm, int(id_intern_raw))
                dialog.destroy()
                messagebox.showinfo('Registro', 'Cuenta creada correctamente')
            except Exception as exc:
                reg_message.set(str(exc))
                reg_message_lbl.grid()

        ttk.Button(d_frame, text='Crear cuenta', style='Primary.TButton', command=submit_register).grid(row=10, column=0, sticky='we', pady=(8, 0))

        reg_username.focus_set()

    ttk.Button(form, text='Entrar', command=handle_login, style='Primary.TButton').grid(row=4, column=0, sticky='we')
    ttk.Button(form, text='Crear compte', command=open_register_dialog, style='Secondary.TButton').grid(row=5, column=0, sticky='we', pady=(8, 0))

    username_entry.focus_set()

    def on_show():
        password_entry.delete(0, tk.END)
        clear_error()

    return frame, on_show
