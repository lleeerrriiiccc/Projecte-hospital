import tkinter as tk
from tkinter import messagebox, ttk

from ..api_client import ApiError
from ..theme import PALETTE
from .base import BaseView


class LoginView(BaseView):
    route = "login"

    def __init__(self, master, app_state, navigate, *args, **kwargs):
        super().__init__(master, app_state, navigate, *args, **kwargs)

        # Login screen is centered around a single card for better focus.
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        card = ttk.Frame(self, style="Card.TFrame", padding=30)
        card.grid(row=0, column=0, padx=16, pady=24)

        title = ttk.Label(card, text="Hospital Control Center", style="Title.TLabel")
        title.grid(row=0, column=0, sticky="w")

        subtitle = ttk.Label(card, text="Autentica't per accedir a l'entorn hospitalari.", style="Muted.TLabel")
        subtitle.grid(row=1, column=0, sticky="w", pady=(6, 16))

        self.message_var = tk.StringVar(value="")
        self.message_label = ttk.Label(card, textvariable=self.message_var, style="Error.TLabel")
        self.message_label.grid(row=2, column=0, sticky="we", pady=(0, 10))
        self.message_label.grid_remove()

        # Form and actions.
        form = ttk.Frame(card)
        form.grid(row=3, column=0, sticky="we")

        ttk.Label(form, text="Usuario").grid(row=0, column=0, sticky="w")
        self.username = ttk.Entry(form, width=32)
        self.username.grid(row=1, column=0, sticky="we", pady=(4, 10))

        ttk.Label(form, text="Contrasena").grid(row=2, column=0, sticky="w")
        self.password = ttk.Entry(form, width=32, show="*")
        self.password.grid(row=3, column=0, sticky="we", pady=(4, 14))

        self.login_btn = ttk.Button(form, text="Entrar", command=self._handle_login, style="Primary.TButton")
        self.login_btn.grid(row=4, column=0, sticky="we")

        register_btn = ttk.Button(form, text="Crear compte", command=self._open_register_dialog, style="Secondary.TButton")
        register_btn.grid(row=5, column=0, sticky="we", pady=(8, 0))

        self.username.focus_set()

    def _set_error(self, text):
        self.message_var.set(text)
        self.message_label.grid()

    def _clear_error(self):
        self.message_var.set("")
        self.message_label.grid_remove()

    def _handle_login(self):
        username = self.username.get().strip()
        password = self.password.get()

        if not username or not password:
            self._set_error("Completa usuario y contrasena.")
            return

        self._clear_error()

        try:
            payload = self.app_state["api"].login(username, password)
            self.app_state["username"] = payload.get("username")
            self.app_state["role"] = payload.get("role")
            self.navigate("home")
        except ApiError as exc:
            self._set_error(str(exc))
        except Exception as exc:
            self._set_error(f"Error de conexion: {exc}")

    def _open_register_dialog(self):
        # Lightweight modal to create users without leaving the login screen.
        dialog = tk.Toplevel(self)
        dialog.title("Registrar usuari")
        dialog.configure(bg=PALETTE["bg"])
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        frame = ttk.Frame(dialog, style="Card.TFrame", padding=18)
        frame.grid(row=0, column=0, padx=14, pady=14)

        ttk.Label(frame, text="Crear compte", style="Title.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))

        fields = [
            ("Usuario", ttk.Entry(frame, width=28)),
            ("Contrasena", ttk.Entry(frame, width=28, show="*")),
            ("Repite contrasena", ttk.Entry(frame, width=28, show="*")),
            ("ID intern", ttk.Entry(frame, width=28)),
        ]

        for idx, (label, widget) in enumerate(fields, start=1):
            ttk.Label(frame, text=label).grid(row=idx * 2 - 1, column=0, sticky="w")
            widget.grid(row=idx * 2, column=0, sticky="we", pady=(4, 8))

        message = tk.StringVar(value="")
        message_lbl = ttk.Label(frame, textvariable=message, style="Error.TLabel")
        message_lbl.grid(row=10, column=0, sticky="we")
        message_lbl.grid_remove()

        def submit_register():
            username = fields[0][1].get().strip()
            password = fields[1][1].get()
            confirm_password = fields[2][1].get()
            id_intern_raw = fields[3][1].get().strip()

            if not id_intern_raw.isdigit():
                message.set("ID intern debe ser numerico")
                message_lbl.grid()
                return

            try:
                self.app_state["api"].register(username, password, confirm_password, int(id_intern_raw))
                dialog.destroy()
                messagebox.showinfo("Registro", "Cuenta creada correctamente")
            except ApiError as exc:
                message.set(str(exc))
                message_lbl.grid()
            except Exception as exc:
                message.set(f"Error: {exc}")
                message_lbl.grid()

        ttk.Button(frame, text="Crear cuenta", style="Primary.TButton", command=submit_register).grid(
            row=11, column=0, sticky="we", pady=(8, 0)
        )

        fields[0][1].focus_set()

    def on_show(self):
        self.password.delete(0, tk.END)
        self._clear_error()
