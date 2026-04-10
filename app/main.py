import flask
import os
from flask import Flask
from flask import request, redirect, url_for, send_from_directory, render_template, make_response
import tools.manager as m
from flask import Flask, jsonify, request
import jwt
import datetime
import datetime



############
# APP CONFIG
############
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'html'))
app = Flask(__name__, template_folder=template_dir)



############
# JWT TOKEN
############
app.secret_key = os.environ.get('FLASK_SECRET')
app.config.update(
                SESSION_COOKIE_HTTPONLY=True,
                SESSION_COOKIE_SAMESITE='Lax')



############
# STATIC FILES
############
@app.route('/css/<path:filename>')
def css(filename):
    css_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'css'))
    return send_from_directory(css_dir, filename)



############
# MAIN ROUTE
############
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return redirect(url_for('login'))
    



############
# LOGIN ROUTE
############
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    if m.login(username, password):
        print("Login successful for user:", username)
        return redirect(url_for('home'))
    else:
        print(m.login(username, password))
        print("Login failed for user:", username)
        return redirect(url_for('login'))



############
# REGISTER ROUTE
############
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', error=None)

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    id_intern_raw = request.form.get('id_intern', '').strip()

    if not username or not password or not confirm_password or not id_intern_raw:
        return render_template('register.html', error='Completa todos los campos.')

    if password != confirm_password:
        return render_template('register.html', error='Las contraseñas no coinciden.')

    if not id_intern_raw.isdigit():
        return render_template('register.html', error='El id_intern debe ser un numero entero.')

    ok, error = m.register(username, password, int(id_intern_raw))
    if ok:
        return redirect(url_for('login'))

    return render_template('register.html', error=error)



############
# HOME ROUTE
############
@app.route('/home')
def home():
    return render_template('home.html') 



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')