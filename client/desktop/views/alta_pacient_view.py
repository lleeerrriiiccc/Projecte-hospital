import datetime
import tkinter as tk
from tkinter import ttk

from .. import api_client as api
from .base import today_iso, parse_iso_date


def create_alta_pacient_view(parent, app_state, navigate):
    frame = ttk.Frame(parent, style='App.TFrame')
    frame.columnconfigure(0, weight=1)

    card = ttk.Frame(frame, style='Card.TFrame', padding=20)
    card.grid(row=0, column=0, sticky='n', padx=16, pady=16)
    card.columnconfigure(1, weight=1)

    ttk.Label(card, text='Alta de Paciente', style='Title.TLabel').grid(row=0, column=0, columnspan=2, sticky='w')
    ttk.Label(card, text='Introduce los datos del paciente.', style='Muted.TLabel').grid(row=1, column=0, columnspan=2, sticky='w', pady=(5, 10))

    status_var = tk.StringVar(value='')
    ttk.Label(card, textvariable=status_var, style='Muted.TLabel').grid(row=2, column=0, columnspan=2, sticky='we', pady=(0, 8))

    # Camps del formulari
    ttk.Label(card, text='Nom').grid(row=3, column=0, sticky='w', pady=3)
    nom_entry = ttk.Entry(card, width=36)
    nom_entry.grid(row=3, column=1, sticky='we', pady=3)

    ttk.Label(card, text='Primer cognom').grid(row=4, column=0, sticky='w', pady=3)
    cognom_entry = ttk.Entry(card, width=36)
    cognom_entry.grid(row=4, column=1, sticky='we', pady=3)

    ttk.Label(card, text='Segon cognom').grid(row=5, column=0, sticky='w', pady=3)
    cognom2_entry = ttk.Entry(card, width=36)
    cognom2_entry.grid(row=5, column=1, sticky='we', pady=3)

    ttk.Label(card, text='Data naixement (YYYY-MM-DD)').grid(row=6, column=0, sticky='w', pady=3)
    data_entry = ttk.Entry(card, width=36)
    data_entry.grid(row=6, column=1, sticky='we', pady=3)
    data_entry.insert(0, '1990-01-01')

    ttk.Label(card, text='Identificador').grid(row=7, column=0, sticky='w', pady=3)
    ident_entry = ttk.Entry(card, width=36)
    ident_entry.grid(row=7, column=1, sticky='we', pady=3)

    buttons = ttk.Frame(card)
    buttons.grid(row=9, column=0, columnspan=2, sticky='we', pady=(10, 0))
    buttons.columnconfigure(0, weight=1)
    buttons.columnconfigure(1, weight=1)

    def submit():
        nom = nom_entry.get().strip()
        cognom = cognom_entry.get().strip()
        cognom2 = cognom2_entry.get().strip()
        data_naixement = data_entry.get().strip()
        identificador = ident_entry.get().strip().upper()

        if not nom or not cognom or not cognom2 or not data_naixement or not identificador:
            status_var.set('Completa todos los campos.')
            return

        try:
            parsed_date = parse_iso_date(data_naixement, 'La fecha debe tener formato YYYY-MM-DD.')
        except ValueError as exc:
            status_var.set(str(exc))
            return

        if parsed_date > datetime.date.today():
            status_var.set('La fecha de nacimiento no puede ser futura.')
            return

        try:
            api.create_patient(nom, cognom, cognom2, data_naixement, identificador)
            status_var.set('Paciente dado de alta correctamente.')
            # Netejar el formulari
            nom_entry.delete(0, tk.END)
            cognom_entry.delete(0, tk.END)
            cognom2_entry.delete(0, tk.END)
            data_entry.delete(0, tk.END)
            data_entry.insert(0, '1990-01-01')
            ident_entry.delete(0, tk.END)
        except Exception as exc:
            status_var.set(str(exc))

    ttk.Button(buttons, text='Guardar', style='Primary.TButton', command=submit).grid(row=0, column=0, sticky='we', padx=(0, 6))
    ttk.Button(buttons, text='Volver', command=lambda: navigate('home')).grid(row=0, column=1, sticky='we', padx=(6, 0))

    def on_show():
        status_var.set('')

    return frame, on_show
