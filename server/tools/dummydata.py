import importlib
import json
import random
import threading
from datetime import date, datetime, time, timedelta
from pathlib import Path

from psycopg2 import sql
from psycopg2.extras import execute_values

import tools.crypt as crypt
import tools.db_driver as db


def _load_faker_factory():
    try:
        faker_module = importlib.import_module('faker')
    except ImportError:
        return None
    return getattr(faker_module, 'Faker', None)


FakerFactory = _load_faker_factory()


BASE_DIR = Path(__file__).resolve().parent
DUMMY_DATA_DIR = BASE_DIR.parent.parent / 'dev' / 'dummy_data' / 'data'


def _load_json(filename):
    with open(DUMMY_DATA_DIR / filename, encoding='utf-8') as file_handle:
        return json.load(file_handle)


ESPECIALITATS = _load_json('especialitats.json')
PLANTES = _load_json('plantes.json')
MAQUINES = _load_json('maquines.json')
MEDICAMENTS = _load_json('medicaments.json')
MALALTIES = _load_json('malalties.json')

_FAKE_ES = None
_FAKE_RU = None

FALLBACK_FIRST_NAMES = (
    'Marc', 'Laura', 'Jordi', 'Marta', 'Nuria', 'Pol', 'Carla', 'Pau', 'Berta', 'Nil',
)
FALLBACK_LAST_NAMES = (
    'Serra', 'Vila', 'Roca', 'Ferrer', 'Costa', 'Pujol', 'Navarro', 'Soler', 'Rius', 'Marti',
)
FALLBACK_CYRILLIC_FIRST_NAMES = (
    'Ivan', 'Nadia', 'Olga', 'Pavel', 'Serguei', 'Anna', 'Irina', 'Dmitri', 'Elena', 'Yuri',
)
FALLBACK_CYRILLIC_LAST_NAMES = (
    'Petrov', 'Sokolov', 'Ivanov', 'Smirnov', 'Volkov', 'Morozov', 'Orlov', 'Kuznetsov', 'Popov', 'Lebedev',
)
FALLBACK_TEXT_FRAGMENTS = (
    'valoracio general favorable',
    'seguiment periodic requerit',
    'incidencia menor resolta',
    'observacions cliniques estables',
    'protocol postoperatori estandard',
    'control preventiu recomanat',
)

TOTAL_PACIENTS = 50000
TOTAL_VISITES = 100000
TOTAL_METGES = 100
TOTAL_INFERMERS = 200
TOTAL_NETEJA = 100
TOTAL_ADMIN = 50
TOTAL_OPERACIONS = 12000
TOTAL_RESERVES = 22000

CYRILLIC_RATIO = 0.015

SOURCE_DATA_FILES = (
    ('especialitats.json', ESPECIALITATS),
    ('plantes.json', PLANTES),
    ('maquines.json', MAQUINES),
    ('medicaments.json', MEDICAMENTS),
    ('malalties.json', MALALTIES),
)

TRUNCATE_TABLES = (
    'recepta',
    'assisteix',
    'inventari',
    'reserva_habitacio',
    'supervisio',
    'assignacio_infermer_planta',
    'operacio',
    'visita',
    'habitacio',
    'quirofan',
    'metge',
    'enfermer',
    'pacient',
    'planta',
    'maquina',
    'medicament',
    'malaltia',
)

TABLE_COUNT_ORDER = (
    'usuaris',
    'personal',
    *TRUNCATE_TABLES,
)

_STATUS_LOCK = threading.Lock()
_JOB_STATUS = {
    'state': 'idle',
    'action': None,
    'message': 'No hi ha cap operacio de dummy data en curs.',
    'username': None,
    'started_at': None,
    'finished_at': None,
}


def _timestamp_text():
    return datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'


def _get_fake_provider(locale):
    global _FAKE_ES, _FAKE_RU

    if FakerFactory is None:
        return None

    if locale == 'ru_RU':
        if _FAKE_RU is None:
            _FAKE_RU = FakerFactory('ru_RU')
        return _FAKE_RU

    if _FAKE_ES is None:
        _FAKE_ES = FakerFactory('es_ES')
    return _FAKE_ES


def _random_phone_number():
    provider = _get_fake_provider('es_ES')
    if provider is not None:
        return provider.phone_number()[:15]
    return str(random.randint(600000000, 799999999))


def _random_username(index):
    provider = _get_fake_provider('es_ES')
    if provider is not None:
        return f"{provider.user_name()}{index}"
    return f'user_{index}_{random.randint(1000, 9999)}'


def _random_text(max_chars):
    provider = _get_fake_provider('es_ES')
    if provider is not None:
        return provider.text(max_nb_chars=max_chars)

    parts = []
    while len(' '.join(parts)) < max_chars:
        parts.append(random.choice(FALLBACK_TEXT_FRAGMENTS))
    return ' '.join(parts)[:max_chars]


def _set_job_status(**updates):
    with _STATUS_LOCK:
        _JOB_STATUS.update(updates)


def get_job_status():
    with _STATUS_LOCK:
        return dict(_JOB_STATUS)


def _source_file_summary():
    summary = []
    for filename, payload in SOURCE_DATA_FILES:
        file_path = DUMMY_DATA_DIR / filename
        summary.append({
            'file': filename,
            'exists': file_path.is_file(),
            'items': len(payload),
        })
    return summary


def _get_table_counts(cursor):
    counts = []
    for table_name in TABLE_COUNT_ORDER:
        cursor.execute(sql.SQL('SELECT COUNT(*) FROM {}').format(sql.Identifier(table_name)))
        counts.append({'table': table_name, 'count': cursor.fetchone()[0]})
    return counts


def _get_missing_tables(cursor):
    cursor.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        """
    )
    existing_tables = {row[0] for row in cursor.fetchall()}
    return [table_name for table_name in TABLE_COUNT_ORDER if table_name not in existing_tables]


def _has_user_role_trigger(cursor):
    cursor.execute(
        """
        SELECT 1
        FROM information_schema.triggers
        WHERE event_object_schema = 'public'
          AND event_object_table = 'usuaris'
          AND trigger_name = 'trigger_create_con_rol'
        LIMIT 1
        """
    )
    return cursor.fetchone() is not None


def _dni_collides_with_dummy_range(dni):
    if not dni:
        return False

    for index in range(TOTAL_METGES + TOTAL_INFERMERS + TOTAL_NETEJA + TOTAL_ADMIN):
        if dni == dni_from_index(index):
            return True
    return False


def _expected_insert_counts(preserve_current_admin=False):
    generated_admins = TOTAL_ADMIN - 1 if preserve_current_admin else TOTAL_ADMIN
    return {
        'personal': TOTAL_METGES + TOTAL_INFERMERS + TOTAL_NETEJA + generated_admins,
        'usuaris': TOTAL_METGES + min(TOTAL_INFERMERS, TOTAL_ADMIN) + generated_admins,
        'pacient': TOTAL_PACIENTS,
        'visita': TOTAL_VISITES,
        'operacio': TOTAL_OPERACIONS,
        'reserva_habitacio': TOTAL_RESERVES,
    }


def get_user_context(username):
    con = None
    cur = None

    try:
        con, cur = db.connect()
        cur.execute(
            """
            SELECT u.id_user, u.username, u.password, u.id_intern, p.tipus_feina, p.dni
            FROM usuaris u
            JOIN personal p ON p.id_intern = u.id_intern
            WHERE LOWER(u.username) = LOWER(%s)
            """,
            (username,),
        )
        row = cur.fetchone()
        if row is None:
            return None

        return {
            'id_user': row[0],
            'username': row[1],
            'password': row[2],
            'id_intern': row[3],
            'tipus_feina': row[4],
            'dni': row[5],
        }

    finally:
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()


def _require_admin_context(username):
    context = get_user_context(username)
    if context is None:
        raise ValueError('L\'usuari autenticat ja no existeix a la base de dades.')
    if context['tipus_feina'] != 'administrador':
        raise PermissionError('Nomes els administradors poden gestionar el dummy data.')
    return context


def _truncate_dummy_tables(cursor):
    cursor.execute(
        sql.SQL('TRUNCATE TABLE {} RESTART IDENTITY').format(
            sql.SQL(', ').join(sql.Identifier(table_name) for table_name in TRUNCATE_TABLES)
        )
    )


def _delete_non_preserved_users(cursor, preserved_username, preserved_id):
    cursor.execute(
        'DELETE FROM usuaris WHERE LOWER(username) <> LOWER(%s)',
        (preserved_username,),
    )
    cursor.execute(
        'DELETE FROM personal WHERE id_intern <> %s',
        (preserved_id,),
    )


def _reset_serial_sequence(cursor, table_name, column_name):
    cursor.execute(
        sql.SQL(
            """
            SELECT setval(
                pg_get_serial_sequence(%s, %s),
                COALESCE(MAX({column_name}), 1),
                COALESCE(MAX({column_name}), 0) <> 0
            )
            FROM {table_name}
            """
        ).format(
            column_name=sql.Identifier(column_name),
            table_name=sql.Identifier(table_name),
        ),
        (table_name, column_name),
    )


def _prepare_empty_dataset(cursor, preserved_username, preserved_id):
    _truncate_dummy_tables(cursor)
    _delete_non_preserved_users(cursor, preserved_username, preserved_id)
    _reset_serial_sequence(cursor, 'personal', 'id_intern')
    _reset_serial_sequence(cursor, 'usuaris', 'id_user')


def validate_dummy_data(username):
    context = _require_admin_context(username)
    con = None
    cur = None

    try:
        con, cur = db.connect()

        job_status = get_job_status()
        table_counts = _get_table_counts(cur)
        count_map = {entry['table']: entry['count'] for entry in table_counts}
        missing_tables = _get_missing_tables(cur)
        trigger_exists = _has_user_role_trigger(cur)
        source_files = _source_file_summary()
        preserved_user = {
            'username': context['username'],
            'id_intern': context['id_intern'],
            'tipus_feina': context['tipus_feina'],
            'dni': context.get('dni'),
        }

        common_issues = []
        generate_issues = []
        delete_issues = []
        warnings = []

        if job_status.get('state') == 'running':
            common_issues.append('Ja hi ha una operacio de dummy data en curs.')

        if missing_tables:
            common_issues.append('Falten taules requerides: ' + ', '.join(missing_tables))

        missing_sources = [item['file'] for item in source_files if not item['exists']]
        if missing_sources:
            generate_issues.append('Falten fitxers de dades dummy: ' + ', '.join(missing_sources))

        if _dni_collides_with_dummy_range(context.get('dni')):
            warnings.append(
                f"El DNI preservat {context.get('dni')} forma part del rang dummy i es reservara automaticament durant la generacio."
            )

        if str(context.get('username', '')).lower().startswith('user_'):
            warnings.append(
                'El username preservat comenca amb el prefix reservat user_. No sol causar xoc, pero convé revisar-lo.'
            )

        if not trigger_exists:
            warnings.append(
                'No s\'ha trobat el trigger trigger_create_con_rol. Els usuaris dummy nous no tindrien rol PostgreSQL associat.'
            )

        empty_sources = [item['file'] for item in source_files if item['items'] == 0]
        if empty_sources:
            warnings.append('Hi ha fitxers de dades dummy buits: ' + ', '.join(empty_sources))

        generate_issues = common_issues + generate_issues
        delete_issues = list(common_issues)

        return {
            'ready_for_generate': len(generate_issues) == 0,
            'ready_for_delete': len(delete_issues) == 0,
            'generate_issues': generate_issues,
            'delete_issues': delete_issues,
            'warnings': warnings,
            'preserved_user': preserved_user,
            'job_status': job_status,
            'table_counts': table_counts,
            'source_files': source_files,
            'expected_insert_counts': _expected_insert_counts(preserve_current_admin=True),
            'users_to_delete': max(count_map.get('usuaris', 0) - 1, 0),
            'personal_to_delete': max(count_map.get('personal', 0) - 1, 0),
            'trigger_exists': trigger_exists,
            'missing_tables': missing_tables,
        }
    finally:
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()


def chunked_insert(cursor, query, rows, page_size=2000):
    buffer = []
    for row in rows:
        buffer.append(row)
        if len(buffer) >= page_size:
            execute_values(cursor, query, buffer, page_size=page_size)
            buffer.clear()
    if buffer:
        execute_values(cursor, query, buffer, page_size=page_size)


def random_birth_date(min_age=0, max_age=95):
    today = date.today()
    min_day = today - timedelta(days=max_age * 365)
    max_day = today - timedelta(days=max(min_age, 0) * 365)
    delta = (max_day - min_day).days
    return min_day + timedelta(days=random.randint(0, max(1, delta)))


def random_recent_date(days_back=3650):
    today = date.today()
    start = today - timedelta(days=days_back)
    delta = (today - start).days
    return start + timedelta(days=random.randint(0, max(1, delta)))


def random_work_time():
    hour = random.randint(8, 20)
    minute = random.choice([0, 10, 20, 30, 40, 50])
    return time(hour=hour, minute=minute)


def dni_from_index(index):
    letters = 'TRWAGMYFPDXBNJZSQVHLCKE'
    number = 10000000 + index
    return f'{number:08d}{letters[number % 23]}'


def _dummy_dni_values(total_needed, reserved_dni=None):
    values = []
    index = 0
    while len(values) < total_needed:
        dni = dni_from_index(index)
        if dni != reserved_dni:
            values.append(dni)
        index += 1
    return values


def maybe_cyrillic_person():
    if random.random() < CYRILLIC_RATIO:
        return (
            random.choice(FALLBACK_CYRILLIC_FIRST_NAMES),
            random.choice(FALLBACK_CYRILLIC_LAST_NAMES),
            random.choice(FALLBACK_CYRILLIC_LAST_NAMES),
        )

    provider = _get_fake_provider('es_ES')
    if provider is not None:
        return provider.first_name(), provider.last_name(), provider.last_name()

    return (
        random.choice(FALLBACK_FIRST_NAMES),
        random.choice(FALLBACK_LAST_NAMES),
        random.choice(FALLBACK_LAST_NAMES),
    )


def create_catalogs(cursor):
    chunked_insert(cursor, 'INSERT INTO planta (nom) VALUES %s', ((planta,) for planta in PLANTES))
    chunked_insert(
        cursor,
        'INSERT INTO maquina (nom, descripcio) VALUES %s',
        ((maquina['nom'], maquina['descripcio']) for maquina in MAQUINES),
    )
    chunked_insert(
        cursor,
        'INSERT INTO medicament (descripcio) VALUES %s',
        ((medicament,) for medicament in MEDICAMENTS),
    )
    chunked_insert(
        cursor,
        'INSERT INTO malaltia (nom) VALUES %s',
        ((malaltia,) for malaltia in MALALTIES),
    )


def create_personal(cursor, preserved_user=None):
    generated_admins = TOTAL_ADMIN - 1 if preserved_user else TOTAL_ADMIN
    total = TOTAL_METGES + TOTAL_INFERMERS + TOTAL_NETEJA + generated_admins
    reserved_dni = preserved_user.get('dni') if preserved_user else None
    dni_values = _dummy_dni_values(total, reserved_dni=reserved_dni)
    rows = []

    for index, dni in enumerate(dni_values):
        nom, cognom, cognom2 = maybe_cyrillic_person()
        if index < TOTAL_METGES:
            tipus = 'metge'
        elif index < TOTAL_METGES + TOTAL_INFERMERS:
            tipus = 'infermer'
        elif index < TOTAL_METGES + TOTAL_INFERMERS + TOTAL_NETEJA:
            tipus = 'tecnic'
        else:
            tipus = 'administrador'

        rows.append(
            (
                nom,
                cognom,
                cognom2,
                random_birth_date(min_age=22, max_age=67),
                _random_phone_number(),
                _random_phone_number(),
                f'{_random_username(index)}@example.com',
                f'{nom.lower()}.{cognom.lower()}.{index}@hospblanes.local'.replace(' ', ''),
                dni,
                tipus,
                random_recent_date(days_back=3650),
            )
        )

    inserted_rows = execute_values(
        cursor,
        """
        INSERT INTO personal (
            nom, cognom, cognom2, data_naixement, telefon, telefon2,
            email, email_intern, dni, tipus_feina, data_alta
        ) VALUES %s
        RETURNING id_intern, tipus_feina
        """,
        rows,
        page_size=1000,
        fetch=True,
    )

    metges = [row[0] for row in inserted_rows if row[1] == 'metge']
    infermers = [row[0] for row in inserted_rows if row[1] == 'infermer']
    admins = [row[0] for row in inserted_rows if row[1] == 'administrador']
    no_metges = [row[0] for row in inserted_rows if row[1] in ('infermer', 'tecnic', 'administrador')]

    execute_values(
        cursor,
        'INSERT INTO metge (id_intern, especialitat, cv) VALUES %s',
        ((metge_id, random.choice(ESPECIALITATS), _random_text(120)) for metge_id in metges),
        page_size=500,
    )
    execute_values(
        cursor,
        'INSERT INTO enfermer (id_intern) VALUES %s',
        ((infermer_id,) for infermer_id in infermers),
        page_size=500,
    )
    execute_values(
        cursor,
        'INSERT INTO supervisio (id_intern, id_metge) VALUES %s',
        ((personal_id, random.choice(metges)) for personal_id in no_metges),
        page_size=1000,
    )

    user_source = metges + infermers[: min(len(infermers), TOTAL_ADMIN)] + admins
    run_suffix = datetime.now().strftime('%Y%m%d%H%M%S')
    dummy_password_hash = crypt.encrypt_password('dummy_password')
    execute_values(
        cursor,
        'INSERT INTO usuaris (username, password, id_intern) VALUES %s',
        ((f'user_{personal_id}_{run_suffix}', dummy_password_hash, personal_id) for personal_id in user_source),
        page_size=1000,
    )

    return metges, infermers


def create_pacients(cursor):
    rows = []
    for index in range(TOTAL_PACIENTS):
        nom, cognom, cognom2 = maybe_cyrillic_person()
        rows.append(
            (
                nom,
                cognom,
                cognom2,
                random_birth_date(min_age=0, max_age=99),
                f'PAC-{index + 1:06d}',
            )
        )

    execute_values(
        cursor,
        'INSERT INTO pacient (nom, cognom, cognom2, data_naixement, identificador) VALUES %s',
        rows,
        page_size=2000,
    )


def create_areas(cursor, infermers):
    cursor.execute('SELECT id_planta FROM planta ORDER BY id_planta')
    plantes = [row[0] for row in cursor.fetchall()]

    habitacions = []
    for planta_id in plantes:
        for number in range(1, 41):
            habitacions.append((planta_id, f'P{planta_id:02d}-{number:03d}'))

    execute_values(
        cursor,
        'INSERT INTO habitacio (id_planta, num_habitacio) VALUES %s',
        habitacions,
        page_size=1000,
    )

    quirofans = []
    for planta_id in plantes:
        for _ in range(2):
            quirofans.append((planta_id,))

    execute_values(cursor, 'INSERT INTO quirofan (id_planta) VALUES %s', quirofans, page_size=200)

    cursor.execute('SELECT id_quirofan FROM quirofan')
    quirofan_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute('SELECT id_maquina FROM maquina')
    maquina_ids = [row[0] for row in cursor.fetchall()]

    inventari_rows = []
    for quirofan_id in quirofan_ids:
        sample_size = min(len(maquina_ids), random.randint(3, 6))
        for maquina_id in random.sample(maquina_ids, k=sample_size):
            inventari_rows.append((quirofan_id, maquina_id))

    execute_values(
        cursor,
        'INSERT INTO inventari (id_quirofan, id_maquina) VALUES %s',
        inventari_rows,
        page_size=500,
    )

    assignacio_rows = []
    for infermer_id in infermers:
        first_planta = random.choice(plantes)
        assignacio_rows.append((infermer_id, first_planta))
        if random.random() < 0.25:
            second_planta = random.choice(plantes)
            if second_planta != first_planta:
                assignacio_rows.append((infermer_id, second_planta))

    execute_values(
        cursor,
        'INSERT INTO assignacio_infermer_planta (id_intern, id_planta) VALUES %s ON CONFLICT DO NOTHING',
        assignacio_rows,
        page_size=1000,
    )


def create_visites_i_receptes(cursor, metges):
    cursor.execute('SELECT id_pacient FROM pacient')
    pacient_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute('SELECT id_malaltia, nom FROM malaltia')
    malalties = cursor.fetchall()
    cursor.execute('SELECT id_medicament FROM medicament')
    medicaments = [row[0] for row in cursor.fetchall()]

    visit_rows = []
    for _ in range(TOTAL_VISITES):
        id_malaltia, nom_malaltia = random.choice(malalties)
        visit_rows.append(
            (
                random.choice(pacient_ids),
                random.choice(metges),
                id_malaltia,
                random_recent_date(days_back=3650),
                random_work_time(),
                f'Simptomes compatibles amb {nom_malaltia}',
            )
        )

    execute_values(
        cursor,
        """
        INSERT INTO visita (
            id_pacient, id_metge, id_malaltia, data_visita, hora_visita, diagnostic
        ) VALUES %s
        """,
        visit_rows,
        page_size=2000,
    )

    cursor.execute('SELECT id_visita FROM visita')
    visita_ids = [row[0] for row in cursor.fetchall()]
    recepta_rows = []
    for visita_id in visita_ids:
        if random.random() < 0.72:
            meds = random.sample(medicaments, k=random.randint(1, min(3, len(medicaments))))
            recepta_rows.extend((visita_id, medicament_id) for medicament_id in meds)

    execute_values(
        cursor,
        'INSERT INTO recepta (id_visita, id_medicament) VALUES %s',
        recepta_rows,
        page_size=2000,
    )


def create_operacions_i_reserves(cursor, metges, infermers):
    cursor.execute('SELECT id_quirofan FROM quirofan')
    quirofans = [row[0] for row in cursor.fetchall()]
    cursor.execute('SELECT id_pacient FROM pacient')
    pacients = [row[0] for row in cursor.fetchall()]
    cursor.execute('SELECT num_habitacio FROM habitacio')
    habitacions = [row[0] for row in cursor.fetchall()]

    operacio_rows = []
    for _ in range(TOTAL_OPERACIONS):
        operacio_rows.append(
            (
                random.choice(quirofans),
                random.choice(pacients),
                random_recent_date(days_back=3650),
                random_work_time(),
                random.choice(
                    [
                        'Apendicectomia',
                        'Artroscopia',
                        'Colangiografia',
                        'Herniorrafia',
                        'Cesariana',
                    ]
                ),
                random.choice(metges),
            )
        )

    execute_values(
        cursor,
        """
        INSERT INTO operacio (
            id_quirofan, id_pacient, data_operacio, hora_operacio, procediment, metge_responsable
        ) VALUES %s
        """,
        operacio_rows,
        page_size=1000,
    )

    cursor.execute('SELECT id_operacio FROM operacio')
    operacio_ids = [row[0] for row in cursor.fetchall()]
    assisteix_rows = []
    for operacio_id in operacio_ids:
        equip = random.sample(infermers, k=min(len(infermers), random.randint(2, 4)))
        assisteix_rows.extend((operacio_id, infermer_id) for infermer_id in equip)

    execute_values(
        cursor,
        'INSERT INTO assisteix (id_operacio, id_intern) VALUES %s',
        assisteix_rows,
        page_size=2000,
    )

    reserva_rows = []
    for _ in range(22000):
        start_date = random_recent_date(days_back=2400)
        end_date = start_date + timedelta(days=random.randint(1, 14))
        reserva_rows.append(
            (
                random.choice(pacients),
                random.choice(habitacions),
                start_date,
                end_date,
            )
        )

    execute_values(
        cursor,
        """
        INSERT INTO reserva_habitacio (id_pacient, num_habitacio, data_inici, data_fi)
        VALUES %s
        ON CONFLICT DO NOTHING
        """,
        reserva_rows,
        page_size=2000,
    )


def validate_counts(cursor):
    checks = {
        'pacient': TOTAL_PACIENTS,
        'visita': TOTAL_VISITES,
        'metge': TOTAL_METGES,
        'enfermer': TOTAL_INFERMERS,
    }

    for table_name, expected in checks.items():
        cursor.execute(sql.SQL('SELECT COUNT(*) FROM {}').format(sql.Identifier(table_name)))
        real = cursor.fetchone()[0]
        if real < expected:
            raise RuntimeError(f'{table_name}: esperat minim {expected}, obtingut {real}')

    cursor.execute(
        """
        SELECT tipus_feina, COUNT(*)
        FROM personal
        GROUP BY tipus_feina
        """
    )
    personal_counts = {row[0]: row[1] for row in cursor.fetchall()}
    required_personal = {
        'metge': TOTAL_METGES,
        'infermer': TOTAL_INFERMERS,
        'tecnic': TOTAL_NETEJA,
        'administrador': TOTAL_ADMIN,
    }

    for tipus_feina, expected in required_personal.items():
        real = personal_counts.get(tipus_feina, 0)
        if real < expected:
            raise RuntimeError(f'personal.{tipus_feina}: esperat minim {expected}, obtingut {real}')


def delete_dummy_data(username):
    preserved_user = _require_admin_context(username)
    con = None
    cur = None

    try:
        con, cur = db.connect()
        _set_job_status(message='Eliminant dades dummy existents...')
        _prepare_empty_dataset(cur, preserved_user['username'], preserved_user['id_intern'])
        con.commit()
    except Exception:
        if con is not None:
            con.rollback()
        raise
    finally:
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()


def generate_dummy_data(username):
    preserved_user = _require_admin_context(username)
    con = None
    cur = None

    random.seed(42)
    if FakerFactory is not None:
        FakerFactory.seed(42)

    try:
        con, cur = db.connect()

        _set_job_status(message='Eliminant dades actuals i preservant l\'administrador autenticat...')
        _prepare_empty_dataset(cur, preserved_user['username'], preserved_user['id_intern'])

        _set_job_status(message='Creant catalegs base...')
        create_catalogs(cur)

        _set_job_status(message='Creant personal, usuaris i relacions dummy...')
        metges, infermers = create_personal(cur, preserved_user=preserved_user)

        _set_job_status(message='Creant pacients dummy...')
        create_pacients(cur)

        _set_job_status(message='Creant plantes, habitacions i quirofans...')
        create_areas(cur, infermers)

        _set_job_status(message='Creant visites i receptes...')
        create_visites_i_receptes(cur, metges)

        _set_job_status(message='Creant operacions i reserves...')
        create_operacions_i_reserves(cur, metges, infermers)

        _set_job_status(message='Validant el volum de dades generat...')
        validate_counts(cur)

        con.commit()
    except Exception:
        if con is not None:
            con.rollback()
        raise
    finally:
        if cur is not None:
            cur.close()
        if con is not None:
            con.close()


def _run_job(action, username):
    try:
        if action == 'generate':
            generate_dummy_data(username)
            _set_job_status(
                state='success',
                message='Dummy data generada correctament.',
                finished_at=_timestamp_text(),
            )
        else:
            delete_dummy_data(username)
            _set_job_status(
                state='success',
                message='Dummy data eliminada correctament.',
                finished_at=_timestamp_text(),
            )
    except PermissionError as exc:
        _set_job_status(state='error', message=str(exc), finished_at=_timestamp_text())
    except Exception as exc:
        _set_job_status(state='error', message=f'Error executant el dummy data: {exc}', finished_at=_timestamp_text())


def _start_job(action, username):
    with _STATUS_LOCK:
        if _JOB_STATUS.get('state') == 'running':
            return False, 'Ja hi ha una operacio de dummy data en curs.'

        _JOB_STATUS.update({
            'state': 'running',
            'action': action,
            'message': 'Preparant l\'operacio de dummy data...',
            'username': username,
            'started_at': _timestamp_text(),
            'finished_at': None,
        })

    worker = threading.Thread(target=_run_job, args=(action, username), daemon=True)
    worker.start()
    return True, get_job_status()


def start_generate_job(username):
    return _start_job('generate', username)


def start_delete_job(username):
    return _start_job('delete', username)