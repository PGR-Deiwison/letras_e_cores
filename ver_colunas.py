import sqlite3

conn = sqlite3.connect('escola.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(notas)')
colunas = cursor.fetchall()
conn.close()

print("Colunas da tabela notas:")
print("-" * 50)
for i, col in enumerate(colunas):
    print(f"{i}: {col[1]:<20} {col[2]:<10}")
