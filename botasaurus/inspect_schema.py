import psycopg2

try:
    conn = psycopg2.connect(dbname='oneextraction', user='postgres', password='7903', host='127.0.0.1', port='5432')
    cur = conn.cursor()

    # Get all tables
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
    tables = cur.fetchall()
    print('TABLES:', [t[0] for t in tables])

    for table in tables:
        tname = table[0]
        cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{tname}' ORDER BY ordinal_position")
        cols = cur.fetchall()
        print(f'\n--- {tname} ---')
        for c in cols:
            print(f'  {c[0]}: {c[1]}')

        cur.execute(f"SELECT COUNT(*) FROM {tname}")
        count = cur.fetchone()[0]
        print(f'  ROW COUNT: {count}')

    cur.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')
