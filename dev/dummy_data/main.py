import json
import random
from datetime import date, datetime, time, timedelta

import psycopg2
from psycopg2.extras import execute_values
from faker import Faker


def json_loader(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


ESPECIALITATS = json_loader("data/especialitats.json")
PLANTES = json_loader("data/plantes.json")
MAQUINES = json_loader("data/maquines.json")
MEDICAMENTS = json_loader("data/medicaments.json")
MALALTIES = json_loader("data/malalties.json")

fake = Faker("es_ES")
fake_ru = Faker("ru_RU")


def conect():
    con = psycopg2.connect(
        host="localhost",
        database="hosp_blanes",
        user="postgres",
        password="postgres",
    )
    con.autocommit = False
    return con, con.cursor()


TOTAL_PACIENTS = 50000
TOTAL_VISITES = 100000
TOTAL_METGES = 100
TOTAL_INFERMERS = 200
TOTAL_NETEJA = 100
TOTAL_ADMIN = 50
TOTAL_OPERACIONS = 12000

CYRILLIC_RATIO = 0.015


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


def dni_from_index(i):
    letters = "TRWAGMYFPDXBNJZSQVHLCKE"
    number = 10000000 + i
    return f"{number:08d}{letters[number % 23]}"


def maybe_cyrillic_person():
    if random.random() < CYRILLIC_RATIO:
        return fake_ru.first_name(), fake_ru.last_name(), fake_ru.last_name()
    return fake.first_name(), fake.last_name(), fake.last_name()


def truncate_all(cursor):
    cursor.execute(
        """
        TRUNCATE TABLE
            recepta,
            assisteix,
            inventari,
            reserva_habitacio,
            supervisio,
            assignacio_infermer_planta,
            usuaris,
            operacio,
            visita,
            habitacio,
            quirofan,
            metge,
            enfermer,
            personal,
            pacient,
            planta,
            maquina,
            medicament,
            malaltia
        RESTART IDENTITY CASCADE
        """
    )


def create_catalogs(cursor):
    chunked_insert(cursor, "INSERT INTO planta (nom) VALUES %s", ((p,) for p in PLANTES))
    chunked_insert(
        cursor,
        "INSERT INTO maquina (nom, descripcio) VALUES %s",
        ((m["nom"], m["descripcio"]) for m in MAQUINES),
    )
    chunked_insert(
        cursor,
        "INSERT INTO medicament (descripcio) VALUES %s",
        ((m,) for m in MEDICAMENTS),
    )
    chunked_insert(cursor, "INSERT INTO malaltia (nom) VALUES %s", ((m,) for m in MALALTIES))


def create_personal(cursor):
    total = TOTAL_METGES + TOTAL_INFERMERS + TOTAL_NETEJA + TOTAL_ADMIN
    rows = []

    for i in range(total):
        nom, cognom, cognom2 = maybe_cyrillic_person()
        if i < TOTAL_METGES:
            tipus = "metge"
        elif i < TOTAL_METGES + TOTAL_INFERMERS:
            tipus = "infermer"
        elif i < TOTAL_METGES + TOTAL_INFERMERS + TOTAL_NETEJA:
            tipus = "tecnic"
        else:
            tipus = "administrador"

        rows.append(
            (
                nom,
                cognom,
                cognom2,
                random_birth_date(min_age=22, max_age=67),
                fake.phone_number()[:15],
                fake.phone_number()[:15],
                f"{fake.user_name()}{i}@example.com",
                f"{nom.lower()}.{cognom.lower()}.{i}@hospblanes.local".replace(" ", ""),
                dni_from_index(i),
                tipus,
                random_recent_date(days_back=3650),
            )
        )

    execute_values(
        cursor,
        """
        INSERT INTO personal (
            nom, cognom, cognom2, data_naixement, telefon, telefon2,
            email, email_intern, dni, tipus_feina, data_alta
        ) VALUES %s
        """,
        rows,
        page_size=1000,
    )

    cursor.execute("SELECT id_intern FROM personal WHERE tipus_feina = 'metge' ORDER BY id_intern")
    metges = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT id_intern FROM personal WHERE tipus_feina = 'infermer' ORDER BY id_intern")
    infermers = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT id_intern FROM personal WHERE tipus_feina IN ('infermer','tecnic','administrador')")
    no_metges = [r[0] for r in cursor.fetchall()]

    execute_values(
        cursor,
        "INSERT INTO metge (id_intern, especialitat, cv) VALUES %s",
        ((m, random.choice(ESPECIALITATS), fake.text(max_nb_chars=120)) for m in metges),
        page_size=500,
    )
    execute_values(
        cursor,
        "INSERT INTO enfermer (id_intern) VALUES %s",
        ((i,) for i in infermers),
        page_size=500,
    )
    execute_values(
        cursor,
        "INSERT INTO supervisio (id_intern, id_metge) VALUES %s",
        ((i, random.choice(metges)) for i in no_metges),
        page_size=1000,
    )
    cursor.execute("SELECT id_intern FROM personal WHERE tipus_feina = 'administrador' ORDER BY id_intern")
    administradors = [r[0] for r in cursor.fetchall()]

    user_source = metges + infermers[: min(len(infermers), TOTAL_ADMIN)] + administradors
    run_suffix = datetime.now().strftime("%Y%m%d%H%M%S")
    execute_values(
        cursor,
        "INSERT INTO usuaris (username, password, id_intern) VALUES %s",
        ((f"user_{i}_{run_suffix}", "dummy_password", i) for i in user_source),
        page_size=1000,
    )

    return metges, infermers


def create_pacients(cursor):
    rows = []
    for i in range(TOTAL_PACIENTS):
        nom, cognom, cognom2 = maybe_cyrillic_person()
        rows.append(
            (
                nom,
                cognom,
                cognom2,
                random_birth_date(min_age=0, max_age=99),
                f"PAC-{i + 1:06d}",
            )
        )
    execute_values(
        cursor,
        "INSERT INTO pacient (nom, cognom, cognom2, data_naixement, identificador) VALUES %s",
        rows,
        page_size=2000,
    )


def create_areas(cursor, infermers):
    cursor.execute("SELECT id_planta FROM planta ORDER BY id_planta")
    plantes = [r[0] for r in cursor.fetchall()]

    habitacions = []
    for planta_id in plantes:
        for n in range(1, 41):
            habitacions.append((planta_id, f"P{planta_id:02d}-{n:03d}"))

    execute_values(
        cursor,
        "INSERT INTO habitacio (id_planta, num_habitacio) VALUES %s",
        habitacions,
        page_size=1000,
    )

    quirofans = []
    for planta_id in plantes:
        for _ in range(2):
            quirofans.append((planta_id,))

    execute_values(cursor, "INSERT INTO quirofan (id_planta) VALUES %s", quirofans, page_size=200)

    cursor.execute("SELECT id_quirofan FROM quirofan")
    quirofan_ids = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT id_maquina FROM maquina")
    maquina_ids = [r[0] for r in cursor.fetchall()]

    inventari_rows = []
    for q in quirofan_ids:
        for m in random.sample(maquina_ids, k=min(len(maquina_ids), random.randint(3, 6))):
            inventari_rows.append((q, m))
    execute_values(
        cursor,
        "INSERT INTO inventari (id_quirofan, id_maquina) VALUES %s",
        inventari_rows,
        page_size=500,
    )

    assignacio_rows = []
    for inf in infermers:
        p1 = random.choice(plantes)
        assignacio_rows.append((inf, p1))
        if random.random() < 0.25:
            p2 = random.choice(plantes)
            if p2 != p1:
                assignacio_rows.append((inf, p2))
    execute_values(
        cursor,
        "INSERT INTO assignacio_infermer_planta (id_intern, id_planta) VALUES %s ON CONFLICT DO NOTHING",
        assignacio_rows,
        page_size=1000,
    )


def create_visites_i_receptes(cursor, metges):
    cursor.execute("SELECT id_pacient FROM pacient")
    pacient_ids = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT id_malaltia, nom FROM malaltia")
    malalties = cursor.fetchall()
    cursor.execute("SELECT id_medicament FROM medicament")
    medicaments = [r[0] for r in cursor.fetchall()]

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
                f"Simptomes compatibles amb {nom_malaltia}",
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

    cursor.execute("SELECT id_visita FROM visita")
    visita_ids = [r[0] for r in cursor.fetchall()]
    recepta_rows = []
    for v in visita_ids:
        if random.random() < 0.72:
            meds = random.sample(medicaments, k=random.randint(1, min(3, len(medicaments))))
            recepta_rows.extend((v, m) for m in meds)
    execute_values(
        cursor,
        "INSERT INTO recepta (id_visita, id_medicament) VALUES %s",
        recepta_rows,
        page_size=2000,
    )


def create_operacions_i_reserves(cursor, metges, infermers):
    cursor.execute("SELECT id_quirofan FROM quirofan")
    quirofans = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT id_pacient FROM pacient")
    pacients = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT num_habitacio FROM habitacio")
    habitacions = [r[0] for r in cursor.fetchall()]

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
                        "Apendicectomia",
                        "Artroscopia",
                        "Colangiografia",
                        "Herniorrafia",
                        "Cesariana",
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

    cursor.execute("SELECT id_operacio FROM operacio")
    operacio_ids = [r[0] for r in cursor.fetchall()]
    assisteix_rows = []
    for op in operacio_ids:
        team = random.sample(infermers, k=min(len(infermers), random.randint(2, 4)))
        assisteix_rows.extend((op, inf) for inf in team)

    execute_values(
        cursor,
        "INSERT INTO assisteix (id_operacio, id_intern) VALUES %s",
        assisteix_rows,
        page_size=2000,
    )

    reserva_rows = []
    for _ in range(22000):
        id_pacient = random.choice(pacients)
        room = random.choice(habitacions)
        start = random_recent_date(days_back=2400)
        end = start + timedelta(days=random.randint(1, 14))
        reserva_rows.append((id_pacient, room, start, end))

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
        "pacient": TOTAL_PACIENTS,
        "visita": TOTAL_VISITES,
        "metge": TOTAL_METGES,
        "enfermer": TOTAL_INFERMERS,
    }
    for table, expected in checks.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        real = cursor.fetchone()[0]
        if real < expected:
            raise RuntimeError(f"{table}: esperat minim {expected}, obtingut {real}")


def main():
    random.seed(42)
    Faker.seed(42)

    con, cursor = conect()
    try:
        print("Netejant dades existents...")
        truncate_all(cursor)

        print("Creant catalegs base...")
        create_catalogs(cursor)

        print("Creant personal i relacions...")
        metges, infermers = create_personal(cursor)

        print("Creant pacients...")
        create_pacients(cursor)

        print("Creant plantes, habitacions i quirofans...")
        create_areas(cursor, infermers)

        print("Creant visites i receptes...")
        create_visites_i_receptes(cursor, metges)

        print("Creant operacions i reserves...")
        create_operacions_i_reserves(cursor, metges, infermers)

        print("Validant minims obligatoris...")
        validate_counts(cursor)

        con.commit()
        print("Dummy data generada correctament.")
    except Exception:
        con.rollback()
        raise
    finally:
        cursor.close()
        con.close()


if __name__ == "__main__":
    main()

