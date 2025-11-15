import sqlite3
from database import init_db

conn = sqlite3.connect('freelance.db')
conn.execute('PRAGMA foreign_keys = ON')
cursor = conn.cursor()

# Удаляем таблицы
cursor.execute('DROP TABLE IF EXISTS Messages')
cursor.execute('DROP TABLE IF EXISTS Reviews')
cursor.execute('DROP TABLE IF EXISTS Applications')
cursor.execute('DROP TABLE IF EXISTS ProjectComments')
cursor.execute('DROP TABLE IF EXISTS Jobs')
cursor.execute('DROP TABLE IF EXISTS Users')
conn.commit()

# Создаем таблицы заново
init_db()

# Проверяем SQL определения
tables = ['Jobs', 'Applications', 'Reviews', 'Messages', 'ProjectComments']
for table in tables:
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
    result = cursor.fetchone()
    if result:
        sql = result[0]
        print(f"\n{table}:")
        print(sql)
        # Проверяем FOREIGN KEY
        cursor.execute(f'PRAGMA foreign_key_list({table})')
        fks = cursor.fetchall()
        print(f"FOREIGN KEYS: {len(fks)}")
        for fk in fks:
            print(f"  - {fk[3]} -> {fk[2]}.{fk[4]}")

conn.close()

