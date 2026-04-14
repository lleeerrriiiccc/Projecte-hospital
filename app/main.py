import flask
import os
from flask import Flask
from flask import request, redirect, url_for, send_from_directory, render_template, make_response, session
import tools.manager as m
from flask import Flask, jsonify, request
import dotenv
import datetime
import datetime



############
# APP CONFIG
############
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'html'))
app = Flask(__name__, template_folder=template_dir)
dotenv.load_dotenv()
app.secret_key = os.getenv("FLASK_SECRET")



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

    ok, error = m.login(username, password)
    if ok:
        session['username'] = username
        return redirect(url_for('home'))
    return render_template('login.html', error=error)



############
# LOGOUT ROUTE
############
@app.route('/logout')
def logout():
    session.pop('username', None)
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
# USER INFO ROUTE
############
@app.route('/me')
def me():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'username': session['username']})



############
# USER INFO ROUTE
############
@app.route('/api/intern/add', methods=['POST'])
def add_inter():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = m.free_intern_id()
    return jsonify(data)



############
# HOME ROUTE
############
@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html') 



############
# NEW PACIENT ROUTE
############
@app.route('/pacient/alta', methods=['GET', 'POST'])
def alta_pacient():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('alta_pacient.html', error=None, success=None)

    nom = request.form.get('nom', '').strip()
    cognom = request.form.get('cognom', '').strip()
    cognom2 = request.form.get('cognom2', '').strip()
    data_naixement_str = request.form.get('data_naixement', '').strip()
    identificador = request.form.get('identificador', '').strip().upper()

    if not nom or not cognom or not cognom2 or not data_naixement_str or not identificador:
        return render_template('alta_pacient.html', error='Completa tots els camps.', success=None)

    try:
        data_naixement = datetime.datetime.strptime(data_naixement_str, '%Y-%m-%d').date()
    except ValueError:
        return render_template('alta_pacient.html', error='La data de naixement no és vàlida.', success=None)

    if data_naixement > datetime.date.today():
        return render_template('alta_pacient.html', error='la data de naixement no pot ser futura.', success=None)

    ok, error = m.new_pacient(nom, cognom, cognom2, data_naixement, identificador)
    if not ok:
        return render_template('alta_pacient.html', error=error, success=None)

    return render_template('alta_pacient.html', error=None, success='Pacient donat d\'alta correctament.')



############
# PERSONAL ROUTE
############
@app.route('/personal/alta', methods=['GET', 'POST'])
def alta_personal():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('alta_personal.html', error=None, success=None)
    nom = request.form.get('nom', '').strip()
    cognom = request.form.get('cognom', '').strip()
    cognom2 = request.form.get('cognom2', '').strip()
    data_naixement_str = request.form.get('data_naixement', '').strip()
    telefon = request.form.get('telefon', '').strip()
    telefon2 = request.form.get('telefon2', '').strip()
    email = request.form.get('email', '').strip()
    email_intern = request.form.get('email_intern', '').strip()
    dni = request.form.get('dni', '').strip().upper()
    tfeina = request.form.get('tipus_feina', '').strip()
    data_alta_str = request.form.get('data_alta', '').strip()
    id_intern = request.form.get('id_intern', '').strip()
    if not nom or not cognom or not cognom2 or not data_naixement_str or not telefon or not email or not email_intern or not dni or not tfeina or not data_alta_str:
        return render_template('alta_personal.html', error='Completa tots els camps obligatoris.', success=None)
    try:
        data_naixement = datetime.datetime.strptime(data_naixement_str, '%Y-%m-%d').date()
    except ValueError:
        return render_template('alta_personal.html', error='La data de naixement no és vàlida.', success=None)
    if data_naixement > datetime.date.today():
        return render_template('alta_personal.html', error='La data de naixement no pot ser futura.', success=None)
    try:
        state, error = m.new_employee(nom, cognom, cognom2, data_naixement, telefon, telefon2, email, email_intern, dni, tfeina, data_alta_str)
        if not state:
            return render_template('alta_personal.html', error=error, success=None)
        return render_template('alta_personal.html', error=None, success='Personal donat d\'alta correctament.')
    except Exception as e:
        return render_template('alta_personal.html', error=str(e), success=None)
    




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)