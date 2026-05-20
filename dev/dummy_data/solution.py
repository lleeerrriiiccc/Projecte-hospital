import psycopg2

try:
    conn = psycopg2.connect(dbname="hosp_blanes")
    cur = conn.cursor()
    
    with open("verification_report.txt", "w") as f:
        # Table counts
        tables = ["pacient", "visita", "metge", "enfermer", "personal"]
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            f.write(f"Count for {table}: {count}\n")
        
        f.write("\nGrouped counts by personal.tipus_feina:\n")
        cur.execute("SELECT tipus_feina, COUNT(*) FROM personal GROUP BY tipus_feina")
        for row in cur.fetchall():
            f.write(f"{row[0]}: {row[1]}\n")
            
        f.write("\nUp to 5 patient names containing Cyrillic chars:\n")
        # Cyrillic range: \u0400-\u04FF
        cur.execute("SELECT nom FROM pacient WHERE nom ~ '[\u0400-\u04FF]' LIMIT 5")
        for row in cur.fetchall():
            f.write(f"{row[0]}\n")
            
    conn.close()
except Exception as e:
    with open("verification_report.txt", "w") as f:
        f.write(f"Error: {str(e)}\n")
