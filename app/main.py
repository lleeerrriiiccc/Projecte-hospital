import datetime
import os
import shutil

import dotenv
from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, session, url_for

import tools.masking as masking
import tools.manager as m




############
# APP CONFIG
############
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'html'))
app = Flask(__name__, template_folder=template_dir)
dotenv.load_dotenv()
app.secret_key = os.getenv("FLASK_SECRET")
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads'))


def _is_json_request():
    return request.is_json or request.path.startswith('/api/')


def _unauthorized_response():
    if _is_json_request():
        return jsonify({'ok': False, 'error': 'Unauthorized'}), 401
    return redirect(url_for('login'))


def _bool_env(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on')



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

    ok, error, tipus = m.login(username, password)
    if ok:
        username = username.lower()
        session['username'] = username
        session['role'] = tipus
        return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'ok': False, 'error': 'Username and password are required.'}), 400

    ok, error, tipus = m.login(username, password)
    if not ok:
        return jsonify({'ok': False, 'error': error}), 401

    username = username.lower()
    session['username'] = username
    session['role'] = tipus
    return jsonify({'ok': True, 'username': username, 'role': tipus})



############
# LOGOUT ROUTE
############
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('username', None)
    session.pop('role', None)
    return jsonify({'ok': True})



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


@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    confirm_password = data.get('confirm_password') or ''
    id_intern_raw = str(data.get('id_intern') or '').strip()

    if not username or not password or not confirm_password or not id_intern_raw:
        return jsonify({'ok': False, 'error': 'Completa todos los campos.'}), 400

    if password != confirm_password:
        return jsonify({'ok': False, 'error': 'Las contraseñas no coinciden.'}), 400

    if not id_intern_raw.isdigit():
        return jsonify({'ok': False, 'error': 'El id_intern debe ser un numero entero.'}), 400

    ok, error = m.register(username, password, int(id_intern_raw))
    if ok:
        return jsonify({'ok': True})

    return jsonify({'ok': False, 'error': error}), 400



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
        return _unauthorized_response()

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


@app.route('/api/pacients', methods=['POST'])
def create_pacient():
    if 'username' not in session:
        return jsonify({'ok': False, 'error': 'Unauthorized'}), 401

    data = request.get_json(silent=True) or {}
    nom = (data.get('nom') or '').strip()
    cognom = (data.get('cognom') or '').strip()
    cognom2 = (data.get('cognom2') or '').strip()
    data_naixement_str = (data.get('data_naixement') or '').strip()
    identificador = (data.get('identificador') or '').strip().upper()

    if not nom or not cognom or not cognom2 or not data_naixement_str or not identificador:
        return jsonify({'ok': False, 'error': 'Completa tots els camps.'}), 400

    try:
        data_naixement = datetime.datetime.strptime(data_naixement_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'ok': False, 'error': 'La data de naixement no és vàlida.'}), 400

    if data_naixement > datetime.date.today():
        return jsonify({'ok': False, 'error': 'La data de naixement no pot ser futura.'}), 400

    ok, error = m.new_pacient(nom, cognom, cognom2, data_naixement, identificador, username=session['username'])
    if not ok:
        return jsonify({'ok': False, 'error': error}), 400

    return jsonify({'ok': True, 'message': 'Pacient donat d\'alta correctament.'})



############
# PERSONAL ROUTE
############
@app.route('/personal/alta', methods=['GET', 'POST'])
def alta_personal():
    if 'username' not in session:
        return _unauthorized_response()

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


@app.route('/api/personal', methods=['POST'])
def create_personal():
    if 'username' not in session:
        return jsonify({'ok': False, 'error': 'Unauthorized'}), 401

    data = request.get_json(silent=True) or {}
    nom = (data.get('nom') or '').strip()
    cognom = (data.get('cognom') or '').strip()
    cognom2 = (data.get('cognom2') or '').strip()
    data_naixement_str = (data.get('data_naixement') or '').strip()
    telefon = (data.get('telefon') or '').strip()
    telefon2 = (data.get('telefon2') or '').strip()
    email = (data.get('email') or '').strip()
    email_intern = (data.get('email_intern') or '').strip()
    dni = (data.get('dni') or '').strip().upper()
    tfeina = (data.get('tipus_feina') or '').strip()
    data_alta_str = (data.get('data_alta') or '').strip()
    especialitat = (data.get('especialitat') or '').strip()
    cv_path = (data.get('cv_path') or '').strip()
    mresp = (data.get('id_metge_supervisor') or '').strip()
    cap_de_planta = bool(data.get('cap_de_planta'))

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
        return jsonify({'ok': False, 'error': 'Completa tots els camps obligatoris.'}), 400

    try:
        data_naixement = datetime.datetime.strptime(data_naixement_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'ok': False, 'error': 'La data de naixement no és vàlida.'}), 400

    if data_naixement > datetime.date.today():
        return jsonify({'ok': False, 'error': 'La data de naixement no pot ser futura.'}), 400

    try:
        if tfeina == 'metge':
            if not especialitat:
                return jsonify({'ok': False, 'error': 'Falta especialitat.'}), 400

            if not cv_path:
                return jsonify({'ok': False, 'error': 'Falta la ruta del CV.'}), 400

            if not os.path.isfile(cv_path):
                return jsonify({'ok': False, 'error': 'El fitxer CV no existeix.'}), 400

            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
            filename = f"{timestamp}_{os.path.basename(cv_path)}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            shutil.copy2(cv_path, save_path)

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
                username=session['username'],
            )
        elif tfeina == 'infermer':
            supervisor = None if cap_de_planta else (mresp or None)
            if supervisor is None and not cap_de_planta:
                return jsonify({'ok': False, 'error': 'Selecciona un metge supervisor o marca cap de planta.'}), 400
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
                mresp=supervisor,
                username=session['username'],
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
                username=session['username'],
            )

        if not state:
            return jsonify({'ok': False, 'error': error}), 400

        return jsonify({'ok': True, 'message': 'Personal donat d\'alta correctament.'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500



############
# REPORT SUPERVISION ROUTE
############
@app.route('/informes/supervisio')
def informes_supervisio():
    if 'username' not in session:
        return _unauthorized_response()
    return render_template('reports/supervisio.html')


############
# REPORT VISITES ROUTE
############
@app.route('/informes/visites')
def informes_visites():
    if 'username' not in session:
        return _unauthorized_response()
    return render_template('reports/visites.html')



############
# REPORT QUIROFANS ROUTE
############
@app.route('/informes/quirofans')
def informes_quirofans():
    if 'username' not in session:
        return _unauthorized_response()
    return render_template('reports/quirofans.html')


############
# REPORT HABITACIONS ROUTE
############
@app.route('/informes/habitacions')
def informes_habitacions():
    if 'username' not in session:
        return _unauthorized_response()
    return render_template('reports/habitacions.html')


############
# REPORT METGE ROUTE
############
@app.route('/informes/metge')
def informes_metge():
    if 'username' not in session:
        return _unauthorized_response()
    return render_template('reports/metge.html')


############
# REPORT APARELLS ROUTE
############
@app.route('/informes/aparells')
def informes_aparells():
    if 'username' not in session:
        return _unauthorized_response()
    return render_template('reports/aparells.html')


############
# REPORT PACIENT ROUTE
############
@app.route('/informes/pacient')
def informes_pacient():
    if 'username' not in session:
        return _unauthorized_response()
    return render_template('reports/pacient.html')


###########################       API ENDPOINTS       ###########################


def api_response(result, data_key='data'):
    ok, payload = result

    if ok:
        payload = _mask_payload(payload)
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
    return jsonify({'username': session['username'], 'role': session.get('role')})


def _mask_payload(payload):
    role = session.get('role')

    if masking.can_view_full_data(role):
        return payload

    if isinstance(payload, dict):
        masked_payload = {}
        for key, value in payload.items():
            if isinstance(value, dict) or isinstance(value, list):
                masked_payload[key] = _mask_payload(value)
            else:
                masked_payload[key] = masking.mask_value(key, value)
        return masked_payload

    if isinstance(payload, list):
        return [_mask_payload(item) for item in payload]

    return payload



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



############
# QUIROFANS REPORT INFO ROUTE
############
@app.route('/api/informes/quirofans')
def get_informes_quirofans():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    date = request.args.get('date', '').strip()
    if not date:
        return jsonify({'error': 'Date parameter is required'}), 400

    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    return api_response(m.get_informes('quirofans', (date,), username=session['username']))


############
# HABITACIONS REPORT INFO ROUTE
############
@app.route('/api/informes/habitacions')
def get_informes_habitacions():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    habitacio = request.args.get('habitacio', '').strip()
    if not habitacio:
        return jsonify({'error': 'Room parameter is required'}), 400

    return api_response(m.get_informes('habitacions', (habitacio,), username=session['username']))


############
# METGE REPORT INFO ROUTE
############
@app.route('/api/informes/metge')
def get_informes_metge():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    metge = request.args.get('metge', '').strip()
    date = request.args.get('date', '').strip()

    if not metge:
        return jsonify({'error': 'Doctor parameter is required'}), 400

    if not date:
        return jsonify({'error': 'Date parameter is required'}), 400

    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    try:
        metge_id = int(metge)
    except ValueError:
        return jsonify({'error': 'Doctor parameter must be a valid integer'}), 400

    return api_response(m.get_informes('metge', (metge_id, date, metge_id, date), username=session['username']))


############
# APARELLS REPORT INFO ROUTE
############
@app.route('/api/informes/aparells')
def get_informes_aparells():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return api_response(m.get_informes('aparells', username=session['username']))



############
# HABITACIONS INFO ROUTE
############
@app.route('/api/habitacions')
def get_habitacions():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return api_response(m.get_habitacions(username=session['username']))


############
# PACIENT INFO ROUTE
############
@app.route('/api/pacients')
def get_pacients():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return api_response(m.get_pacients(username=session['username']))


############
# PACIENT REPORT INFO ROUTE
############
@app.route('/api/informes/pacient')
def get_informes_pacient():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    pacient = request.args.get('pacient', '').strip()
    if not pacient:
        return jsonify({'error': 'Patient parameter is required'}), 400

    try:
        pacient_id = int(pacient)
    except ValueError:
        return jsonify({'error': 'Patient parameter must be a valid integer'}), 400

    return api_response(m.get_informes('pacient', (pacient_id, pacient_id, pacient_id, pacient_id), username=session['username']))



if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '443'))
    debug = _bool_env('FLASK_DEBUG', default=True)
    use_ssl = _bool_env('FLASK_USE_SSL', default=True)

    cert = os.getenv('CERT')
    key = os.getenv('KEY')
    ssl_context = (cert, key) if use_ssl and cert and key else None

    app.run(debug=debug, host=host, port=port, ssl_context=ssl_context)