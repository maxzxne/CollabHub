#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('freelance.db')
c = conn.cursor()
c.execute('PRAGMA foreign_keys = ON')

print("="*60)
print("ПРОВЕРКА СВЯЗЕЙ В БАЗЕ ДАННЫХ")
print("="*60)

# Ожидаемые связи из дипломной работы
expected = {
    'Jobs': [
        ('creator_email', 'Users', 'email')
    ],
    'Applications': [
        ('job_id', 'Jobs', 'id'),
        ('freelancer_email', 'Users', 'email')
    ],
    'Reviews': [
        ('job_id', 'Jobs', 'id'),
        ('freelancer_email', 'Users', 'email'),
        ('client_email', 'Users', 'email')
    ],
    'Messages': [
        ('sender_email', 'Users', 'email'),
        ('receiver_email', 'Users', 'email'),
        ('job_id', 'Jobs', 'id')
    ],
    'ProjectComments': [
        ('job_id', 'Jobs', 'id'),
        ('user_email', 'Users', 'email')
    ]
}

total_expected = sum(len(v) for v in expected.values())
total_found = 0

for table, expected_fks in expected.items():
    c.execute(f'PRAGMA foreign_key_list({table})')
    found_fks = c.fetchall()
    
    print(f"\n{table}:")
    print(f"  Ожидается: {len(expected_fks)} связей")
    print(f"  Найдено: {len(found_fks)} связей")
    
    found_pairs = [(fk[3], fk[2], fk[4]) for fk in found_fks]
    
    for exp_fk in expected_fks:
        if exp_fk in found_pairs:
            print(f"    [OK] {exp_fk[0]} -> {exp_fk[1]}.{exp_fk[2]}")
            total_found += 1
        else:
            print(f"    [MISSING] {exp_fk[0]} -> {exp_fk[1]}.{exp_fk[2]}")
    
    # Проверяем лишние связи
    for found_fk in found_pairs:
        if found_fk not in expected_fks:
            print(f"    [EXTRA] {found_fk[0]} -> {found_fk[1]}.{found_fk[2]}")

print("\n" + "="*60)
print(f"ИТОГО: {total_found}/{total_expected} связей создано")
print("="*60)

if total_found == total_expected:
    print("\n[SUCCESS] ВСЕ СВЯЗИ СООТВЕТСТВУЮТ ОПИСАНИЮ ИЗ ДИПЛОМНОЙ РАБОТЫ!")
    print("База данных готова для создания ER-диаграммы в DBeaver.")
else:
    print(f"\n[WARNING] Не все связи созданы ({total_found} из {total_expected})")

conn.close()

