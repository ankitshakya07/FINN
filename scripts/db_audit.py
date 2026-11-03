import sqlite3, json, os
db_path = os.path.join(os.path.dirname(__file__), '..', 'finn.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()
tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('TABLES AND ROW COUNTS:')
for t in tables:
    n = t[0]
    cnt = c.execute(f'SELECT COUNT(*) FROM "{n}"').fetchone()[0]
    print(f'  {n}: {cnt} rows')
print()
companies = c.execute('SELECT ticker,name FROM companies LIMIT 20').fetchall()
print('SAMPLE COMPANIES:')
for row in companies:
    print(f'  {row[0]}: {row[1]}')
print()
ps = c.execute('SELECT DISTINCT source FROM prices').fetchall()
print('PRICE SOURCES:', [r[0] for r in ps])
ans = c.execute('SELECT DISTINCT source FROM announcements').fetchall()
print('ANNOUNCEMENT SOURCES:', [r[0] for r in ans])
print()
# fundamentals
fnd = c.execute('SELECT DISTINCT ticker, source FROM company_fundamentals LIMIT 10').fetchall()
print('FUNDAMENTALS (ticker, source):')
for row in fnd:
    print(f'  {row[0]}, {row[1]}')
print()
# commitments
cmts = c.execute('SELECT DISTINCT ticker, demo_mode FROM company_commitments LIMIT 10').fetchall()
print('COMMITMENTS (ticker, demo_mode):')
for row in cmts:
    print(f'  {row[0]}, demo={row[1]}')
print()
# management changes
mc = c.execute('SELECT COUNT(*) FROM management_change_events').fetchone()[0]
print(f'Management change events: {mc}')
# filings
fl = c.execute('SELECT COUNT(*) FROM filings').fetchone()[0]
print(f'Filings: {fl}')
# LLM cache
lc = c.execute('SELECT COUNT(*) FROM llm_cache').fetchone()[0]
print(f'LLM cache entries: {lc}')
conn.close()

