# EVERYTHING SQL

import sqlite3

DB_NAME = "expenses.db"

def init_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                category TEXT,
                amount REAL,
                description TEXT,
                split_count INTEGER,
                deleted INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("DB Init Error:", e)
        return False

def fetch_expenses():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, date, category, amount, description, split_count
        FROM expenses
        WHERE deleted = 0
        ORDER BY date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_expenses(date, category, amount, description, split_count):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO expenses (date, category, amount, description, split_count, deleted)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (date, category, amount, description, split_count))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Add Error:", e)
        return False

def delete_expenses(expense_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE expenses
            SET deleted = 1
            WHERE id = ?
        """, (expense_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Delete Error:", e)
        return False
