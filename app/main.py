import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
import tools.manager as m


# ========================
# MAIN SCREEN
# ========================
class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Gestio hospitalaria")
        self.state("zoomed")  # Pantalla completa

        container = ttk.Frame(self)
        container.pack(fill=BOTH, expand=YES)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (LoginScreen, RegisterScreen, HomeScreen):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginScreen)
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


# ========================
# LOGIN SCREEN
# ========================
#Clase que representa la pantalla de login, hereda de ttk.Frame 
class LoginScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=20)

        # ========================
        # TARJETA CENTRADA
        # ========================
        tarjeta = ttk.Frame(self, padding=40)
        tarjeta.place(relx=0.5, rely=0.5, anchor="center")

        # ========================
        # TITOL
        # ========================
        ttk.Label(
            tarjeta,
            text="Iniciar sessió",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 15))

        # ========================
        # USUARI
        # ========================
        ttk.Label(tarjeta, text="Usuari").pack(anchor="w")
        self.username = ttk.Entry(tarjeta, width=30)
        self.username.pack(pady=5)

        # ========================
        # PASSWORD
        # ========================
        ttk.Label(tarjeta, text="Contrasenya").pack(anchor="w")
        self.password = ttk.Entry(tarjeta, width=30, show="*")
        self.password.pack(pady=5)

        # ========================
        # BOTO LOGIN
        # ========================
        ttk.Button(
            tarjeta,
            text="Iniciar sesió",
            bootstyle="success",
            width=25,
            command=lambda: controller.show_frame(HomeScreen) if m.login(self.username.get(), self.password.get()) else tk.messagebox.showerror("Error", "Credencials incorrectes")
        ).pack(pady=20)
        
        # ========================
        # BOTO REGISTRE
        # ========================
        ttk.Button(
            tarjeta,
            text="Registrar-se",
            bootstyle="secondary",
            width=25,
            command=lambda: controller.show_frame(RegisterScreen)
        ).pack()



# ========================
# REGISTER SCREEN
# ========================
class RegisterScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=20)

        # ========================
        # TARJETA CENTRADA
        # ========================
        tarjeta = ttk.Frame(self, padding=40)
        tarjeta.place(relx=0.5, rely=0.5, anchor="center")

        # ========================
        # TITOL
        # ========================
        ttk.Label(
            tarjeta,
            text="Registrar-se",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 15))

        # ========================
        # USUARI
        # ========================
        ttk.Label(tarjeta, text="Usuari").pack(anchor="w")
        self.username = ttk.Entry(tarjeta, width=30)
        self.username.pack(pady=5)

        # ========================
        # PASSWORD
        # ========================
        ttk.Label(tarjeta, text="Contrasenya").pack(anchor="w")
        self.password = ttk.Entry(tarjeta, width=30, show="*")
        self.password.pack(pady=5)

        # ========================
        # PASSWORD
        # ========================
        ttk.Label(tarjeta, text="Repetir contrasenya").pack(anchor="w")
        self.password_repeat = ttk.Entry(tarjeta, width=30, show="*")
        self.password_repeat.pack(pady=5)

        # ========================
        # BOTO LOGIN
        # ========================
        ttk.Button(
            tarjeta,
            text="Tornar al login",
            bootstyle="secondary",
            width=25,
            command=lambda: controller.show_frame(LoginScreen)
        ).pack(pady=20)
        
        # ========================
        # BOTO REGISTRE
        # ========================
        ttk.Button(
            tarjeta,
            text="Registrar-se",
            bootstyle="success",
            width=25,
            command=lambda: controller.show_frame(RegisterScreen)
        ).pack()

# ========================
# HOME SCREEN
# ========================
class HomeScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=20)

        ttk.Label(self, text="Home", font=("Segoe UI", 18)).pack(pady=10)

        ttk.Button(
            self,
            text="Cerrar sesión",
            bootstyle="danger",
            command=lambda: controller.show_frame(LoginScreen)
        ).pack()


# ========================
# BUCLE PRINCIPAL
# ========================
if __name__ == "__main__":
    app = App()
    app.mainloop()