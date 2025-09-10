import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# Hash passwords before inserting sample users
sample_users = [
    ('John Doe', 'john@example.com', generate_password_hash('password123')),
    ('Jane Smith', 'jane@example.com', generate_password_hash('secret456')),
    ('Bob Johnson', 'bob@example.com', generate_password_hash('qwerty789'))
]

# Use INSERT OR IGNORE to prevent errors if the script is run multiple times
cursor.executemany("INSERT OR IGNORE INTO users (name, email, password) VALUES (?, ?, ?)", sample_users)
conn.commit()
conn.close()

print("Database initialized with sample data.")