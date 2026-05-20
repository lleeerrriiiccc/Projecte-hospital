import psycopg2
import re

try:
    conn = psycopg2.connect(
        host="localhost",
        database="hosp_blanes",
        user="postgres",
        password="postgres"
    )
    cur = conn.cursor()

    with open("verification_report.txt", "w", encoding="utf-8") as f:
        f.write("Table Counts:\n")
        tables = ['pacient', 'visita', 'metge', 'enfermer', 'personal']
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            f.write(f"{table}: {count}\n")

        f.write("\nGrouped counts by personal.tipus_feina:\n")
        cur.execute("SELECT tipus_feina, COUNT(*) FROM personal GROUP BY tipus_feina")
        for tipus, count in cur.fetchall():
            f.write(f"{tipus}: {count}\n")

        f.write("\n5 rows with Cyrillic names from pacient:\n")
        # Using POSIX regex in PostgreSQL for Cyrillic chars
        cur.execute("SELECT nom FROM pacient WHERE nom ~ '[\u0400-\u04FF]' LIMIT 5")
        rows = cur.fetchall()
        for row in rows:
            f.write(f"{row[0]}\n")

    cur.close()
    conn.close()
    print("Verification report generated successfully.")

except Exception as e:
    print(f"Error: {e}")
