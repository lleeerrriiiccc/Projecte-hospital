import datetime  # Llibreria per gestionar les dates
import os  # Llibreria per gestionar les rutes i fitxers

import dotenv  # Llibreria per gestionar les variables d'entorn
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)  # Llibreria per gestionar el servidor web i les rutes

import tools.masking as masking  # Llibreria per gestionar el masking de dades sensibles
import tools.manager as m  # Llibreria per gestionar la lògica i les consultes a la base de dades



#Configuracio principal de l'aplicacio Flask
############
# APP CONFIG
############
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'html'))  # Ruta absoluta al directori de plantilles HTML
app = Flask(__name__, template_folder=template_dir)  # Creacio de l'objecte Flask amb la ruta de les plantilles HTML
dotenv.load_dotenv()  # Carrega les variables d'entorn des del fitxer .env
app.secret_key = os.getenv("FLASK_SECRET")  # Clau secreta per gestionar les sessions, obtinguda de les variables d'entorn
app.config['UPLOAD_FOLDER'] = "c:\\Users\\el160\\Desktop\\1r ASIX\\Projecte-hospital\\app\\uploads"  # Ruta on es guardaran els fitxers pujats (com els CVs dels metges)


###########################       STATIC ENDPOINTS       ###########################


# ruta desde on es serveixen els arxius estatics css
############
# STATIC FILES
############
@app.route('/css/<path:filename>')  # definicio de la ruta per servir els arxius css
def css(filename):
    css_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'css'))  # definicio de la ruta absoluta al directori css
    return send_from_directory(css_dir, filename)  # serveix el fitxer css sol·licitat des del directori css




###########################       APP ENDPOINTS       ###########################


# ruta principal de l'aplicació, redirigeix a la pàgina de login
############
# MAIN ROUTE
############
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return redirect(url_for('login'))


# ruta de login
############
# LOGIN ROUTE
############
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')  # si el metode es get es mostra la pagina de login

    username = request.form.get('username')  # recull el nom d'usuari del formulari de login
    password = request.form.get('password')  # recull la contrasenya del formulari de login

    ok, error, tipus = m.login(username, password)  # executa la funcio de login desde el manager i desempaqueta els resultats en tres variables: ok (boolean que indica si el login ha sigut correcte), error (missatge d'error en cas de que el login hagi fallat) i tipus (tipus d'usuari, com metge, infermer, admin, etc.)
    if ok:  # si el login ha sigut correcte
        username = username.lower()  # converteix el nom d'usuari a minuscules per estandaritzar-lo
        session['username'] = username  # guarda el nom d'usuari a la sessio per mantenir l'estat de login
        session['role'] = tipus
        return redirect(url_for('home'))  # retorna el usuari a la pagina principal de l'aplicacio (home)
    return render_template('login.html', error=error)  # si el login ha fallat, es torna a mostrar la pagina de login pero amb un missatge d'error que explica el motiu del fallit del login (com per exemple "usuari o contrasenya incorrectes")


#ruta de logout, que elimina les dades de la sessio i redirigeix a la pagina de login
############
# LOGOUT ROUTE
############
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))


#ruta de registre de nous usuaris, que permet crear nous comptes d'usuari per accedir a l'aplicacio
############
# REGISTER ROUTE
############
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Si el metode es GET, es mostra la pagina de registre per crear un nou compte d'usuari
    if request.method == 'GET':
        return render_template('register.html', error=None)

    # Si el metode es POST, es recullen les dades del formulari de registre
    #  i s'intenta crear un nou compte d'usuari amb aquestes dades. 
    # Es realitzen diverses comprovacions per assegurar que les dades son correctes 
    # (com que tots els camps estiguin complets, que les contrasenyes coincideixin, 
    # que el id_intern sigui un numero enter, etc.) i si tot es correcte, 
    # es crida a la funcio de registre del manager per crear el nou compte d'usuari. 
    # Si el registre es correcte, es redirigeix a la pagina de login per que l'usuari
    # pugui iniciar sessio amb el nou compte creat. Si hi ha algun error en les dades o 
    # en el procés de registre, es torna a mostrar la pagina de registre pero amb un missatge d'error
    #  que explica el motiu del fallit del registre.
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


#  ruta de la pagina principal (home) que es mostra després de iniciar sessio correctament,
#  i que permet accedir a les diferents funcionalitats de l'aplicacio com donar d'alta nous
#  pacients o personal, veure els informes, etc.
############
# HOME ROUTE
############
@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')


# ruta per donar d'alta nous pacients a la base de dades, que recull les dades del formulari d'alta de pacient,
#  realitza diverses comprovacions per assegurar que les dades son correctes (com que tots els camps estiguin complets,
#  que la data de naixement sigui valida i no sea futura, etc.) i si tot es correcte, crida a la funcio de alta de pacient
#  del manager per crear el nou pacient a la base de dades. Si l'alta es correcte, es mostra un missatge d'exit a la pagina 
# d'alta de pacient. Si hi ha algun error en les dades o en el procés d'alta, es torna a mostrar la pagina d'alta de pacient
#  pero amb un missatge d'error que explica el motiu del fallit de l'alta.
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


# ruta per donar d'alta nous membres del personal a la base de dades, que recull les dades del formulari d'alta de personal,
#  realitza diverses comprovacions per assegurar que les dades son correctes 
# (com que tots els camps obligatoris estiguin complets, que la data de naixement sigui valida i no sigui futura, etc.)

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
    # Dades opcionals: especialitat (metge) i CV.
    # Si no venen al formulari, es gestionen com a buides dins del manager.
    especialitat = request.form.get('especialitat', '').strip()
    cv = request.files.get('cv')

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


# ruta per veure els informes de supervisio, que simplement comprova que l'usuari estigui loguejat i si es així,
#  mostra la pagina d'informes de supervisio
############
# REPORT SUPERVISION ROUTE
############
@app.route('/informes/supervisio')
def informes_supervisio():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('reports/supervisio.html')

# ruta per veure els informes de visites, que simplement comprova que l'usuari estigui loguejat i si es així,
#  mostra la pagina d'informes de visites
############
# REPORT VISITES ROUTE
############
@app.route('/informes/visites')
def informes_visites():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('reports/visites.html')


# ruta per veure els informes de quirofans, que simplement comprova que l'usuari estigui loguejat i si es així,
#  mostra la pagina d'informes de quirofans
############
# REPORT QUIROFANS ROUTE
############
@app.route('/informes/quirofans')
def informes_quirofans():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('reports/quirofans.html')

# ruta per veure els informes d'habitacions, que simplement comprova que l'usuari estigui loguejat i si es així,
#  mostra la pagina d'informes d'habitacions
############
# REPORT HABITACIONS ROUTE
############
@app.route('/informes/habitacions')
def informes_habitacions():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('reports/habitacions.html')

# ruta per veure els informes de metge, que simplement comprova que l'usuari estigui loguejat i si es així,
#  mostra la pagina d'informes de metge
############
# REPORT METGE ROUTE
############
@app.route('/informes/metge')
def informes_metge():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('reports/metge.html')

# ruta per veure els informes d'aparells, que simplement comprova que l'usuari estigui loguejat i si es així,
#  mostra la pagina d'informes d'aparells
############
# REPORT APARELLS ROUTE
############
@app.route('/informes/aparells')
def informes_aparells():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('reports/aparells.html')

# ruta per veure els informes de pacient, que simplement comprova que l'usuari estigui loguejat i si es así,
#  mostra la pagina d'informes de pacient
############
# REPORT PACIENT ROUTE
############
@app.route('/informes/pacient')
def informes_pacient():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('reports/pacient.html')


###########################       API ENDPOINTS       ###########################

# funcio per gestionar el control d'errors i el format de les respostes de les API, 
# que rep com a parametre el resultat d'una consulta a la base de dades 
# (en format de tupla amb un boolean que indica si la consulta ha sigut correcta o no,
#  i el payload o missatge d'error corresponent) i retorna una resposta JSON amb un format estandaritzat
#  que indica si la consulta ha sigut correcta o no, i inclou el payload de dades en cas de que la consulta
#  hagi sigut correcta, o un missatge d'error en cas de que la consulta hagi fallat.
#  Aquesta funcio també gestiona el masking de dades sensibles segons el rol de l'usuari loguejat,
#  cridant a la funcio _mask_payload per aplicar el masking necessari al payload de dades abans de retornar-lo a l'usuari.
def api_response(result, data_key='data'):
    ok, payload = result

    if ok:
        payload = _mask_payload(payload)
        return jsonify({'ok': True, data_key: payload})

    error_text = str(payload)
    status_code = 403 if 'permis' in error_text.lower() or 'permission' in error_text.lower() else 400
    return jsonify({'ok': False, 'error': error_text}), status_code

# ruta per veure la informació de l'usuari loguejat, que comprova que l'usuari estigui loguejat i si es així,
#  retorna una resposta JSON amb el nom d'usuari i el rol de l'usuari loguejat. Aquesta ruta pot ser utilitzada per la part frontend de l'aplicacio per mostrar el nom d'usuari i el rol a la interfície, o per gestionar el control d'accés a diferents funcionalitats segons el rol de l'usuari.
############
# USER INFO ROUTE
############
@app.route('/me')
def me():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'username': session['username'], 'role': session.get('role')})


# funcio auxiliar que aplica masking de dades sensibles de manera recursiva
# segons el rol de l'usuari loguejat. Si el rol te permisos complets,
# retorna el payload original; si no, mascara camps sensibles en dicts i llistes.
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


# ruta per veure la informació dels metges, que simplement comprova que l'usuari estigui loguejat i si es així,
#  retorna una resposta JSON amb la informació dels metges obtinguda a través de la funcio get_metges del manager. 
# Aquesta ruta pot ser utilitzada per la part frontend de l'aplicacio per mostrar la llista de metges a la interfície, 
# o per gestionar altres funcionalitats relacionades amb els metges.
############
# DOC INFO ROUTE
############
@app.route('/api/metges')
def get_metges():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return api_response(m.get_metges(username=session['username']))



# ruta per veure els informes de supervisio via API,
# que comprova autenticacio i retorna les dades en format JSON estandaritzat.
############
# SUPERVISION REPORT INFO ROUTE
############
@app.route('/api/informes/supervisio')
def get_informes_supervisio():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return api_response(m.get_informes('supervisio', username=session['username']))



# ruta per veure els informes de visites via API,
# validant el parametre de data abans d'executar la consulta.
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



# ruta per veure els informes de quirofans via API,
# validant el parametre de data en format YYYY-MM-DD.
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



# ruta per veure els informes d'habitacions via API,
# demanant el parametre d'habitacio per filtrar resultats.
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



# ruta per veure els informes de metge via API,
# validant tant el metge (enter) com la data de consulta.
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



# ruta per veure els informes d'aparells via API,
# retornant les dades segons els permisos del rol autenticat.
############
# APARELLS REPORT INFO ROUTE
############
@app.route('/api/informes/aparells')
def get_informes_aparells():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return api_response(m.get_informes('aparells', username=session['username']))



# ruta per obtenir la llista d'habitacions via API,
# amb resposta JSON i control d'acces per sessio activa.
############
# HABITACIONS INFO ROUTE
############
@app.route('/api/habitacions')
def get_habitacions():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return api_response(m.get_habitacions(username=session['username']))



# ruta per obtenir la llista de pacients via API,
# aplicant masking automatic segons el rol de l'usuari.
############
# PACIENT INFO ROUTE
############
@app.route('/api/pacients')
def get_pacients():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return api_response(m.get_pacients(username=session['username']))



# ruta per veure els informes d'un pacient via API,
# validant l'identificador numeric abans de consultar dades.
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
    app.run(debug=True, host='0.0.0.0', port=443, ssl_context=(os.getenv('CERT'), os.getenv('KEY')))