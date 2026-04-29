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
    return redirect(url_for('login'))


############
# LOGIN ROUTE
############
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not username or not password:
        return render_template('login.html', error='Completa todos los campos.')

    ok, error, tipus = m.login(username, password)
    if ok:
        session['username'] = username.lower()
        session['role'] = tipus
        return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'ok': False, 'error': 'Username and password are required.'}), 400

    ok, error, tipus = m.login(username, password)
    if not ok:
        return jsonify({'ok': False, 'error': error}), 401

    session['username'] = username.lower()
    session['role'] = tipus
    return jsonify({'ok': True, 'username': username.lower(), 'role': tipus})


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
    confirm = request.form.get('confirm_password', '')
    id_intern = request.form.get('id_intern', '').strip()

    if not username or not password or not confirm or not id_intern:
        return render_template('register.html', error='Completa todos los campos.')

    if password != confirm:
        return render_template('register.html', error='Las contraseñas no coinciden.')

    if not id_intern.isdigit():
        return render_template('register.html', error='El id_intern debe ser un numero entero.')

    ok, error = m.register(username, password, int(id_intern))
    if ok:
        return redirect(url_for('login'))
    return render_template('register.html', error=error)


@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    confirm = data.get('confirm_password', '')
    id_intern = str(data.get('id_intern', '')).strip()

    if not username or not password or not confirm or not id_intern:
        return jsonify({'ok': False, 'error': 'Completa todos los campos.'}), 400

    if password != confirm:
        return jsonify({'ok': False, 'error': 'Las contraseñas no coinciden.'}), 400

    if not id_intern.isdigit():
        return jsonify({'ok': False, 'error': 'El id_intern debe ser un numero entero.'}), 400

    ok, error = m.register(username, password, int(id_intern))
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
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('alta_pacient.html')

    nom = request.form.get('nom', '').strip()
    cognom = request.form.get('cognom', '').strip()
    cognom2 = request.form.get('cognom2', '').strip()
    data_naixement = request.form.get('data_naixement', '').strip()
    identificador = request.form.get('identificador', '').strip().upper()

    if not nom or not cognom or not cognom2 or not data_naixement or not identificador:
        return render_template('alta_pacient.html', error='Completa tots els camps.')

    try:
        parsed_date = datetime.datetime.strptime(data_naixement, '%Y-%m-%d').date()
    except ValueError:
        return render_template('alta_pacient.html', error='La data de naixement no és vàlida.')

    if parsed_date > datetime.date.today():
        return render_template('alta_pacient.html', error='La data de naixement no pot ser futura.')

    ok, error = m.new_pacient(nom, cognom, cognom2, parsed_date, identificador, username=session.get('username'))
    if ok:
        return render_template('alta_pacient.html', success="Pacient donat d'alta correctament.")
    return render_template('alta_pacient.html', error=error)


@app.route('/api/pacients', methods=['POST'])
def create_pacient():
    if 'username' not in session:
        return jsonify({'ok': False, 'error': 'Unauthorized'}), 401

    data = request.get_json(silent=True) or {}
    nom = data.get('nom', '').strip()
    cognom = data.get('cognom', '').strip()
    cognom2 = data.get('cognom2', '').strip()
    data_naixement = data.get('data_naixement', '').strip()
    identificador = data.get('identificador', '').strip().upper()

    if not nom or not cognom or not cognom2 or not data_naixement or not identificador:
        return jsonify({'ok': False, 'error': 'Completa tots els camps.'}), 400

    try:
        parsed_date = datetime.datetime.strptime(data_naixement, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'ok': False, 'error': 'La data de naixement no és vàlida.'}), 400

    if parsed_date > datetime.date.today():
        return jsonify({'ok': False, 'error': 'La data de naixement no pot ser futura.'}), 400

    ok, error = m.new_pacient(nom, cognom, cognom2, parsed_date, identificador, username=session.get('username'))
    if ok:
        return jsonify({'ok': True, 'message': "Pacient donat d'alta correctament."})
    return jsonify({'ok': False, 'error': error}), 400


############
# PERSONAL ROUTE
############
@app.route('/personal/alta', methods=['GET', 'POST'])
def alta_personal():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('alta_personal.html')

    nom = request.form.get('nom', '').strip()
    cognom = request.form.get('cognom', '').strip()
    cognom2 = request.form.get('cognom2', '').strip()
    data_naixement = request.form.get('data_naixement', '').strip()
    telefon = request.form.get('telefon', '').strip()
    telefon2 = request.form.get('telefon2', '').strip()
    email = request.form.get('email', '').strip()
    email_intern = request.form.get('email_intern', '').strip()
    dni = request.form.get('dni', '').strip().upper()
    tipus_feina = request.form.get('tipus_feina', '').strip()
    data_alta = request.form.get('data_alta', '').strip()
    especialitat = request.form.get('especialitat', '').strip()
    id_metge_supervisor = request.form.get('id_metge_supervisor', '').strip() or None
    cap_de_planta = request.form.get('cap_de_planta', 'false').lower() in ('1', 'true', 'yes', 'on')

    if not nom or not cognom or not cognom2 or not data_naixement or not telefon or not email or not email_intern or not dni or not tipus_feina or not data_alta:
        return render_template('alta_personal.html', error='Completa tots els camps obligatoris.')

    try:
        datetime.datetime.strptime(data_naixement, '%Y-%m-%d')
    except ValueError:
        return render_template('alta_personal.html', error='La data de naixement no és vàlida.')

    if tipus_feina == 'metge' and not especialitat:
        return render_template('alta_personal.html', error='Falta especialitat.')

    cv_file_path = None
    if tipus_feina == 'metge':
        uploaded_cv = request.files.get('cv')
        if uploaded_cv is None or not uploaded_cv.filename:
            return render_template('alta_personal.html', error='Falten especialitat o CV.')
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        cv_file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_cv.filename)
        uploaded_cv.save(cv_file_path)

    if tipus_feina == 'infermer' and cap_de_planta:
        id_metge_supervisor = None

    ok, error = m.new_employee(
        nom, cognom, cognom2, data_naixement, telefon, telefon2,
        email, email_intern, dni, tipus_feina, data_alta,
        especialitat=especialitat or None,
        cv=cv_file_path,
        mresp=id_metge_supervisor,
        username=session.get('username'),
    )
    if ok:
        return render_template('alta_personal.html', success="Personal donat d'alta correctament.")
    return render_template('alta_personal.html', error=error)


@app.route('/api/personal', methods=['POST'])
def create_personal():
    if 'username' not in session:
        return jsonify({'ok': False, 'error': 'Unauthorized'}), 401

    data = request.get_json(silent=True) or {}
    nom = data.get('nom', '').strip()
    cognom = data.get('cognom', '').strip()
    cognom2 = data.get('cognom2', '').strip()
    data_naixement = data.get('data_naixement', '').strip()
    telefon = data.get('telefon', '').strip()
    telefon2 = data.get('telefon2', '').strip()
    email = data.get('email', '').strip()
    email_intern = data.get('email_intern', '').strip()
    dni = data.get('dni', '').strip().upper()
    tipus_feina = data.get('tipus_feina', '').strip()
    data_alta = data.get('data_alta', '').strip()
    especialitat = data.get('especialitat', '').strip()
    cv_path = data.get('cv_path', '').strip()
    id_metge_supervisor = data.get('id_metge_supervisor') or None
    cap_de_planta = bool(data.get('cap_de_planta', False))

    if not nom or not cognom or not cognom2 or not data_naixement or not telefon or not email or not email_intern or not dni or not tipus_feina or not data_alta:
        return jsonify({'ok': False, 'error': 'Completa tots els camps obligatoris.'}), 400

    try:
        parsed_date = datetime.datetime.strptime(data_naixement, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'ok': False, 'error': 'La data de naixement no és vàlida.'}), 400

    if parsed_date > datetime.date.today():
        return jsonify({'ok': False, 'error': 'La data de naixement no pot ser futura.'}), 400

    if tipus_feina == 'metge' and not especialitat:
        return jsonify({'ok': False, 'error': 'Falta especialitat.'}), 400

    cv_file_path = None
    if tipus_feina == 'metge':
        if not cv_path or not os.path.isfile(cv_path):
            return jsonify({'ok': False, 'error': 'El fitxer CV no existeix.'}), 400
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        filename = f"{timestamp}_{os.path.basename(cv_path)}"
        cv_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        shutil.copy2(cv_path, cv_file_path)

    if tipus_feina == 'infermer' and cap_de_planta:
        id_metge_supervisor = None

    ok, error = m.new_employee(
        nom, cognom, cognom2, data_naixement, telefon, telefon2,
        email, email_intern, dni, tipus_feina, data_alta,
        especialitat=especialitat or None,
        cv=cv_file_path,
        mresp=id_metge_supervisor,
        username=session.get('username'),
    )
    if ok:
        return jsonify({'ok': True, 'message': "Personal donat d'alta correctament."})
    return jsonify({'ok': False, 'error': error}), 400


############
# REPORT PAGES
############
@app.route('/informes/supervisio')
def informes_supervisio():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('reports/supervisio.html')


@app.route('/informes/visites')
def informes_visites():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('reports/visites.html')


@app.route('/informes/quirofans')
def informes_quirofans():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('reports/quirofans.html')


@app.route('/informes/habitacions')
def informes_habitacions():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('reports/habitacions.html')


@app.route('/informes/metge')
def informes_metge():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('reports/metge.html')


@app.route('/informes/aparells')
def informes_aparells():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('reports/aparells.html')


@app.route('/informes/pacient')
def informes_pacient():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('reports/pacient.html')


############
# USER INFO ROUTE
############
@app.route('/me')
def me():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'username': session.get('username'), 'role': session.get('role')})


############
# API DATA ENDPOINTS
############
def mask_and_return(result):
    ok, payload = result
    if ok:
        payload = masking.mask_payload(payload, session.get('role'))
        return jsonify({'ok': True, 'data': payload})
    error_text = str(payload)
    status_code = 403 if 'permis' in error_text.lower() else 400
    return jsonify({'ok': False, 'error': error_text}), status_code


@app.route('/api/metges')
def get_metges():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return mask_and_return(m.get_metges(username=session.get('username')))


@app.route('/api/informes/supervisio')
def get_informes_supervisio():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return mask_and_return(m.get_informes('supervisio', username=session.get('username')))


@app.route('/api/informes/visites')
def get_informes_visites():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    date_value = request.args.get('date', '').strip()
    if not date_value:
        return jsonify({'error': 'Date parameter is required'}), 400
    try:
        datetime.datetime.strptime(date_value, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    return mask_and_return(m.get_informes('visites', (date_value,), username=session.get('username')))


@app.route('/api/informes/quirofans')
def get_informes_quirofans():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    date_value = request.args.get('date', '').strip()
    if not date_value:
        return jsonify({'error': 'Date parameter is required'}), 400
    try:
        datetime.datetime.strptime(date_value, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    return mask_and_return(m.get_informes('quirofans', (date_value,), username=session.get('username')))


@app.route('/api/informes/habitacions')
def get_informes_habitacions():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    habitacio = request.args.get('habitacio', '').strip()
    if not habitacio:
        return jsonify({'error': 'Room parameter is required'}), 400
    return mask_and_return(m.get_informes('habitacions', (habitacio,), username=session.get('username')))


@app.route('/api/informes/metge')
def get_informes_metge():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    metge_id = request.args.get('metge', '').strip()
    date_value = request.args.get('date', '').strip()
    if not metge_id or not date_value:
        return jsonify({'error': 'metge and date parameters are required'}), 400
    try:
        metge_id = int(metge_id)
        datetime.datetime.strptime(date_value, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid parameters'}), 400
    return mask_and_return(m.get_informes('metge', (metge_id, date_value, metge_id, date_value), username=session.get('username')))


@app.route('/api/informes/aparells')
def get_informes_aparells():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return mask_and_return(m.get_informes('aparells', username=session.get('username')))


@app.route('/api/habitacions')
def get_habitacions():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return mask_and_return(m.get_habitacions(username=session.get('username')))


@app.route('/api/pacients')
def get_pacients():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return mask_and_return(m.get_pacients(username=session.get('username')))


@app.route('/api/informes/pacient')
def get_informes_pacient():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    pacient_id = request.args.get('pacient', '').strip()
    if not pacient_id:
        return jsonify({'error': 'Patient parameter is required'}), 400
    try:
        pacient_id = int(pacient_id)
    except ValueError:
        return jsonify({'error': 'Patient parameter must be a valid integer'}), 400
    return mask_and_return(m.get_informes('pacient', (pacient_id, pacient_id, pacient_id, pacient_id), username=session.get('username')))


if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'true').strip().lower() in ('1', 'true', 'yes', 'on')
    app.run(debug=debug, host=host, port=port)





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


PATIENT_TEMPLATE = 'alta_pacient.html'
EMPLOYEE_TEMPLATE = 'alta_personal.html'
REGISTER_TEMPLATE = 'register.html'

PATIENT_REQUIRED_FIELDS = ('nom', 'cognom', 'cognom2', 'data_naixement', 'identificador')
EMPLOYEE_REQUIRED_FIELDS = (
    'nom',
    'cognom',
    'cognom2',
    'data_naixement',
    'telefon',
    'email',
    'email_intern',
    'dni',
    'tipus_feina',
    'data_alta',
)


def _get_text(source, key, uppercase=False):
    value = source.get(key) if source is not None else ''
    text = str(value or '').strip()
    return text.upper() if uppercase else text


def _get_bool(source, key):
    value = source.get(key) if source is not None else False
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on')


def _render_form(template_name, error=None, success=None):
    return render_template(template_name, error=error, success=success)


def _json_ok(message=None, **extra):
    payload = {'ok': True}
    if message is not None:
        payload['message'] = message
    payload.update(extra)
    return jsonify(payload)


def _json_error(message, status=400):
    return jsonify({'ok': False, 'error': message}), status


def _plain_json_error(message, status=400):
    return jsonify({'error': message}), status


def _action_response(ok, error, success_message, template_name=None, failure_status=400):
    if ok:
        if template_name is not None:
            return _render_form(template_name, error=None, success=success_message)
        return _json_ok(message=success_message)

    if template_name is not None:
        return _render_form(template_name, error=error, success=None)
    return _json_error(error, failure_status)


def _set_logged_user(username, role):
    session['username'] = username.lower()
    session['role'] = role


def _clear_logged_user():
    session.pop('username', None)
    session.pop('role', None)


def _current_username():
    return session.get('username')


def _require_login():
    if 'username' not in session:
        return _unauthorized_response()
    return None


def _require_plain_api_login():
    if 'username' not in session:
        return _plain_json_error('Unauthorized', 401)
    return None


def _validate_required(data, required_fields, message):
    for field_name in required_fields:
        if not data.get(field_name):
            raise ValueError(message)


def _parse_date_text(value, invalid_message, future_message=None):
    try:
        parsed_date = datetime.datetime.strptime(str(value).strip(), '%Y-%m-%d').date()
    except ValueError as exc:
        raise ValueError(invalid_message) from exc

    if future_message and parsed_date > datetime.date.today():
        raise ValueError(future_message)

    return parsed_date


def _read_login_data(source):
    return {
        'username': _get_text(source, 'username'),
        'password': source.get('password') or '',
    }


def _validate_login_data(data):
    _validate_required(data, ('username', 'password'), 'Completa todos los campos.')


def _read_register_data(source):
    return {
        'username': _get_text(source, 'username'),
        'password': source.get('password') or '',
        'confirm_password': source.get('confirm_password') or '',
        'id_intern': _get_text(source, 'id_intern'),
    }


def _validate_register_data(data):
    _validate_required(data, ('username', 'password', 'confirm_password', 'id_intern'), 'Completa todos los campos.')

    if data['password'] != data['confirm_password']:
        raise ValueError('Las contraseñas no coinciden.')

    if not data['id_intern'].isdigit():
        raise ValueError('El id_intern debe ser un numero entero.')


def _read_patient_data(source):
    return {
        'nom': _get_text(source, 'nom'),
        'cognom': _get_text(source, 'cognom'),
        'cognom2': _get_text(source, 'cognom2'),
        'data_naixement': _get_text(source, 'data_naixement'),
        'identificador': _get_text(source, 'identificador', uppercase=True),
    }


def _validate_patient_data(data, future_message='La data de naixement no pot ser futura.'):
    _validate_required(data, PATIENT_REQUIRED_FIELDS, 'Completa tots els camps.')
    data['data_naixement'] = _parse_date_text(
        data['data_naixement'],
        'La data de naixement no és vàlida.',
        future_message,
    )


def _create_patient_record(data):
    return m.new_pacient(
        data['nom'],
        data['cognom'],
        data['cognom2'],
        data['data_naixement'],
        data['identificador'],
        username=_current_username(),
    )


def _read_employee_data(source):
    return {
        'nom': _get_text(source, 'nom'),
        'cognom': _get_text(source, 'cognom'),
        'cognom2': _get_text(source, 'cognom2'),
        'data_naixement': _get_text(source, 'data_naixement'),
        'telefon': _get_text(source, 'telefon'),
        'telefon2': _get_text(source, 'telefon2'),
        'email': _get_text(source, 'email'),
        'email_intern': _get_text(source, 'email_intern'),
        'dni': _get_text(source, 'dni', uppercase=True),
        'tipus_feina': _get_text(source, 'tipus_feina'),
        'data_alta': _get_text(source, 'data_alta'),
        'especialitat': _get_text(source, 'especialitat'),
        'cv_path': _get_text(source, 'cv_path'),
        'id_metge_supervisor': _get_text(source, 'id_metge_supervisor'),
        'cap_de_planta': _get_bool(source, 'cap_de_planta'),
    }


def _validate_employee_data(data, require_supervisor=False):
    _validate_required(data, EMPLOYEE_REQUIRED_FIELDS, 'Completa tots els camps obligatoris.')
    data['data_naixement'] = _parse_date_text(
        data['data_naixement'],
        'La data de naixement no és vàlida.',
        'La data de naixement no pot ser futura.',
    )

    if data['tipus_feina'] == 'metge' and not data['especialitat']:
        raise ValueError('Falta especialitat.')

    if data['tipus_feina'] == 'infermer':
        if data['cap_de_planta']:
            data['id_metge_supervisor'] = None
        elif not data['id_metge_supervisor']:
            if require_supervisor:
                raise ValueError('Selecciona un metge supervisor o marca cap de planta.')
            data['id_metge_supervisor'] = None


def _save_uploaded_cv(uploaded_file):
    if uploaded_file is None or not getattr(uploaded_file, 'filename', ''):
        raise ValueError('Falten especialitat o CV.')

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
    uploaded_file.save(save_path)
    return save_path


def _copy_cv_file(cv_path):
    if not cv_path:
        raise ValueError('Falta la ruta del CV.')

    if not os.path.isfile(cv_path):
        raise ValueError('El fitxer CV no existeix.')

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    filename = f"{timestamp}_{os.path.basename(cv_path)}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    shutil.copy2(cv_path, save_path)
    return save_path


def _create_employee_record(data, cv_file_path=None):
    return m.new_employee(
        data['nom'],
        data['cognom'],
        data['cognom2'],
        data['data_naixement'],
        data['telefon'],
        data['telefon2'],
        data['email'],
        data['email_intern'],
        data['dni'],
        data['tipus_feina'],
        data['data_alta'],
        especialitat=data.get('especialitat') or None,
        cv=cv_file_path,
        mresp=data.get('id_metge_supervisor') or None,
        username=_current_username(),
    )


def _render_report_page(template_name):
    unauthorized = _require_login()
    if unauthorized:
        return unauthorized
    return render_template(f'reports/{template_name}.html')


def _get_required_arg(name, label):
    value = _get_text(request.args, name)
    if not value:
        raise ValueError(f'{label} parameter is required')
    return value


def _get_required_date_arg():
    date_value = _get_required_arg('date', 'Date')

    try:
        datetime.datetime.strptime(date_value, '%Y-%m-%d')
    except ValueError as exc:
        raise ValueError('Invalid date format. Use YYYY-MM-DD') from exc

    return date_value


def _get_required_int_arg(name, label):
    value = _get_required_arg(name, label)

    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f'{label} parameter must be a valid integer') from exc



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

    data = _read_login_data(request.form)

    try:
        _validate_login_data(data)
    except ValueError as exc:
        return render_template('login.html', error=str(exc))

    ok, error, tipus = m.login(data['username'], data['password'])
    if ok:
        _set_logged_user(data['username'], tipus)
        return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/api/login', methods=['POST'])
def api_login():
    data = _read_login_data(request.get_json(silent=True) or {})

    try:
        _validate_login_data(data)
    except ValueError:
        return _json_error('Username and password are required.')

    ok, error, tipus = m.login(data['username'], data['password'])
    if not ok:
        return _json_error(error, 401)

    _set_logged_user(data['username'], tipus)
    return jsonify({'ok': True, 'username': data['username'].lower(), 'role': tipus})



############
# LOGOUT ROUTE
############
@app.route('/logout')
def logout():
    _clear_logged_user()
    return redirect(url_for('login'))


@app.route('/api/logout', methods=['POST'])
def api_logout():
    _clear_logged_user()
    return _json_ok()



############
# REGISTER ROUTE
############
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template(REGISTER_TEMPLATE, error=None)

    data = _read_register_data(request.form)

    try:
        _validate_register_data(data)
    except ValueError as exc:
        return render_template(REGISTER_TEMPLATE, error=str(exc))

    ok, error = m.register(data['username'], data['password'], int(data['id_intern']))
    if ok:
        return redirect(url_for('login'))

    return render_template(REGISTER_TEMPLATE, error=error)


@app.route('/api/register', methods=['POST'])
def api_register():
    data = _read_register_data(request.get_json(silent=True) or {})

    try:
        _validate_register_data(data)
    except ValueError as exc:
        return _json_error(str(exc))

    ok, error = m.register(data['username'], data['password'], int(data['id_intern']))
    if ok:
        return _json_ok()

    return _json_error(error)



############
# HOME ROUTE
############
@app.route('/home')
def home():
    unauthorized = _require_login()
    if unauthorized:
        return unauthorized
    return render_template('home.html')



############
# NEW PACIENT ROUTE
############
@app.route('/pacient/alta', methods=['GET', 'POST'])
def alta_pacient():
    unauthorized = _require_login()
    if unauthorized:
        return unauthorized

    if request.method == 'GET':
        return _render_form(PATIENT_TEMPLATE)

    data = _read_patient_data(request.form)

    try:
        _validate_patient_data(data, 'la data de naixement no pot ser futura.')
    except ValueError as exc:
        return _render_form(PATIENT_TEMPLATE, error=str(exc), success=None)

    ok, error = _create_patient_record(data)
    return _action_response(ok, error, 'Pacient donat d\'alta correctament.', template_name=PATIENT_TEMPLATE)


@app.route('/api/pacients', methods=['POST'])
def create_pacient():
    unauthorized = _require_login()
    if unauthorized:
        return unauthorized

    data = _read_patient_data(request.get_json(silent=True) or {})

    try:
        _validate_patient_data(data)
    except ValueError as exc:
        return _json_error(str(exc))

    ok, error = _create_patient_record(data)
    return _action_response(ok, error, 'Pacient donat d\'alta correctament.')



############
# PERSONAL ROUTE
############
@app.route('/personal/alta', methods=['GET', 'POST'])
def alta_personal():
    unauthorized = _require_login()
    if unauthorized:
        return unauthorized

    if request.method == 'GET':
        return _render_form(EMPLOYEE_TEMPLATE)

    data = _read_employee_data(request.form)
    uploaded_cv = request.files.get('cv')

    try:
        _validate_employee_data(data)
        cv_file_path = _save_uploaded_cv(uploaded_cv) if data['tipus_feina'] == 'metge' else None
        state, error = _create_employee_record(data, cv_file_path)
        return _action_response(state, error, 'Personal donat d\'alta correctament.', template_name=EMPLOYEE_TEMPLATE)
    except Exception as exc:
        return _render_form(EMPLOYEE_TEMPLATE, error=str(exc), success=None)


@app.route('/api/personal', methods=['POST'])
def create_personal():
    unauthorized = _require_login()
    if unauthorized:
        return unauthorized

    data = _read_employee_data(request.get_json(silent=True) or {})

    try:
        _validate_employee_data(data, require_supervisor=True)
        cv_file_path = _copy_cv_file(data['cv_path']) if data['tipus_feina'] == 'metge' else None
        state, error = _create_employee_record(data, cv_file_path)
        return _action_response(state, error, 'Personal donat d\'alta correctament.')
    except ValueError as exc:
        return _json_error(str(exc))
    except Exception as exc:
        return _json_error(str(exc), 500)



############
# REPORT SUPERVISION ROUTE
############
@app.route('/informes/supervisio')
def informes_supervisio():
    return _render_report_page('supervisio')


############
# REPORT VISITES ROUTE
############
@app.route('/informes/visites')
def informes_visites():
    return _render_report_page('visites')



############
# REPORT QUIROFANS ROUTE
############
@app.route('/informes/quirofans')
def informes_quirofans():
    return _render_report_page('quirofans')


############
# REPORT HABITACIONS ROUTE
############
@app.route('/informes/habitacions')
def informes_habitacions():
    return _render_report_page('habitacions')


############
# REPORT METGE ROUTE
############
@app.route('/informes/metge')
def informes_metge():
    return _render_report_page('metge')


############
# REPORT APARELLS ROUTE
############
@app.route('/informes/aparells')
def informes_aparells():
    return _render_report_page('aparells')


############
# REPORT PACIENT ROUTE
############
@app.route('/informes/pacient')
def informes_pacient():
    return _render_report_page('pacient')


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
    unauthorized = _require_plain_api_login()
    if unauthorized:
        return unauthorized
    return jsonify({'username': _current_username(), 'role': session.get('role')})


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
    unauthorized = _require_plain_api_login()
    if unauthorized:
        return unauthorized
    return api_response(m.get_metges(username=_current_username()))



############
# SUPERVISION REPORT INFO ROUTE
############
@app.route('/api/informes/supervisio')
def get_informes_supervisio():
    unauthorized = _require_plain_api_login()
    if unauthorized:
        return unauthorized
    return api_response(m.get_informes('supervisio', username=_current_username()))



############
# VISITES REPORT INFO ROUTE
############
@app.route('/api/informes/visites')
def get_informes_visites():
    unauthorized = _require_plain_api_login()
    if unauthorized:
        return unauthorized
    try:
        date_value = _get_required_date_arg()
    except ValueError as exc:
        return _plain_json_error(str(exc))

    return api_response(m.get_informes('visites', (date_value,), username=_current_username()))



############
# QUIROFANS REPORT INFO ROUTE
############
@app.route('/api/informes/quirofans')
def get_informes_quirofans():
    unauthorized = _require_plain_api_login()
    if unauthorized:
        return unauthorized
    try:
        date_value = _get_required_date_arg()
    except ValueError as exc:
        return _plain_json_error(str(exc))

    return api_response(m.get_informes('quirofans', (date_value,), username=_current_username()))


############
# HABITACIONS REPORT INFO ROUTE
############
@app.route('/api/informes/habitacions')
def get_informes_habitacions():
    unauthorized = _require_plain_api_login()
    if unauthorized:
        return unauthorized

    try:
        habitacio = _get_required_arg('habitacio', 'Room')
    except ValueError as exc:
        return _plain_json_error(str(exc))

    return api_response(m.get_informes('habitacions', (habitacio,), username=_current_username()))


############
# METGE REPORT INFO ROUTE
############
@app.route('/api/informes/metge')
def get_informes_metge():
    unauthorized = _require_plain_api_login()
    if unauthorized:
        return unauthorized

    try:
        metge_id = _get_required_int_arg('metge', 'Doctor')
        date_value = _get_required_date_arg()
    except ValueError as exc:
        return _plain_json_error(str(exc))

    return api_response(m.get_informes('metge', (metge_id, date_value, metge_id, date_value), username=_current_username()))


############
# APARELLS REPORT INFO ROUTE
############
@app.route('/api/informes/aparells')
def get_informes_aparells():
    unauthorized = _require_plain_api_login()
    if unauthorized:
        return unauthorized
    return api_response(m.get_informes('aparells', username=_current_username()))



############
# HABITACIONS INFO ROUTE
############
@app.route('/api/habitacions')
def get_habitacions():
    unauthorized = _require_plain_api_login()
    if unauthorized:
        return unauthorized
    return api_response(m.get_habitacions(username=_current_username()))


############
# PACIENT INFO ROUTE
############
@app.route('/api/pacients')
def get_pacients():
    unauthorized = _require_plain_api_login()
    if unauthorized:
        return unauthorized
    return api_response(m.get_pacients(username=_current_username()))


############
# PACIENT REPORT INFO ROUTE
############
@app.route('/api/informes/pacient')
def get_informes_pacient():
    unauthorized = _require_plain_api_login()
    if unauthorized:
        return unauthorized

    try:
        pacient_id = _get_required_int_arg('pacient', 'Patient')
    except ValueError as exc:
        return _plain_json_error(str(exc))

    return api_response(m.get_informes('pacient', (pacient_id, pacient_id, pacient_id, pacient_id), username=_current_username()))



if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = _bool_env('FLASK_DEBUG', default=True)
    use_ssl = _bool_env('FLASK_USE_SSL', default=False)

    cert = os.getenv('CERT')
    key = os.getenv('KEY')
    ssl_context = (cert, key) if use_ssl and cert and key else None

    app.run(debug=debug, host=host, port=port, ssl_context=ssl_context)