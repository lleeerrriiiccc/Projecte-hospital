import datetime
import os

import dotenv
from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, session, url_for

import tools.manager as m




############
# APP CONFIG
############
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'html'))
app = Flask(__name__, template_folder=template_dir)
dotenv.load_dotenv()
app.secret_key = os.getenv("FLASK_SECRET")
app.config['UPLOAD_FOLDER'] = "c:\\Users\\el160\\Desktop\\1r ASIX\\Projecte-hospital\\app\\uploads"



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

    ok, error, type = m.login(username, password)
    if ok:
        session['username'] = username
        session['type'] = type
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

    ok, error = m.new_pacient(nom, cognom, cognom2, data_naixement, identificador, username=session['username'])
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
    mresp = request.form.get('id_metge_supervisor', '').strip()
    try:
        especialitat = request.form.get('especialitat', '').strip()
        cv = request.files.get('cv')
    except:
        pass

    if (
        not nom
        or not cognom
        or not cognom2
        or not data_naixement_str
        or not telefon
        or not email
        or not email_intern
        or not dni
        or not tfeina
        or not data_alta_str
    ):
        return render_template('alta_personal.html', error='Completa tots els camps obligatoris.', success=None)

    try:
        data_naixement = datetime.datetime.strptime(data_naixement_str, '%Y-%m-%d').date()
    except ValueError:
        return render_template('alta_personal.html', error='La data de naixement no és vàlida.', success=None)

    if data_naixement > datetime.date.today():
        return render_template('alta_personal.html', error='La data de naixement no pot ser futura.', success=None)

    try:
        if tfeina == 'metge':
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filename = cv.filename if cv else None
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) if filename else None
            cv.save(save_path)
            state, error = m.new_employee(
                nom,
                cognom,
                cognom2,
                data_naixement,
                telefon,
                telefon2,
                email,
                email_intern,
                dni,
                tfeina,
                data_alta_str,
                especialitat,
                save_path,
                username=session['username']
            )
        elif tfeina == 'infermer':
            mresp = mresp if mresp else None
            state, error = m.new_employee(
                    nom,
                    cognom,
                    cognom2,
                    data_naixement,
                    telefon,
                    telefon2,
                    email,
                    email_intern,
                    dni,
                    tfeina,
                    data_alta_str,
                    mresp=mresp,
                    username=session['username']
                )

        else:
            state, error = m.new_employee(
                nom,
                cognom,
                cognom2,
                data_naixement,
                telefon,
                telefon2,
                email,
                email_intern,
                dni,
                tfeina,
                data_alta_str,
                username=session['username']
            )

        if not state:
            return render_template('alta_personal.html', error=error, success=None)

        return render_template('alta_personal.html', error=None, success='Personal donat d\'alta correctament.')
    except Exception as e:
        return render_template('alta_personal.html', error=str(e), success=None)



############
# REPORT SUPERVISION ROUTE
############
@app.route('/informes/supervisio')
def informes_supervisio():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('reports/supervisio.html')


############
# REPORT VISITES ROUTE
############
@app.route('/informes/visites')
def informes_visites():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('reports/visites.html')



###########################       API ENDPOINTS       ###########################


def api_response(result, data_key='data'):
    ok, payload = result

    if ok:
        return jsonify({'ok': True, data_key: payload})

    error_text = str(payload)
    status_code = 403 if 'permis' in error_text.lower() or 'permission' in error_text.lower() else 400
    return jsonify({'ok': False, 'error': error_text}), status_code


############
# USER INFO ROUTE
############
@app.route('/me')
def me():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'username': session['username']})



############
# DOC INFO ROUTE
############
@app.route('/api/metges')
def get_metges():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return api_response(m.get_metges(username=session['username']))



############
# SUPERVISION REPORT INFO ROUTE
############
@app.route('/api/informes/supervisio')
def get_informes_supervisio():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return api_response(m.get_informes('supervisio', username=session['username']))



############
# VISITES REPORT INFO ROUTE
############
@app.route('/api/informes/visites')
def get_informes_visites():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    date = request.args.get('date', '').strip()
    if not date:
        return jsonify({'error': 'Date parameter is required'}), 400

    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    return api_response(m.get_informes('visites', (date,), username=session['username']))



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)