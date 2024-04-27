import sqlite3
import bcrypt
import os

def sys_init():
    # Since no hardcoded filepaths are requested, I chose to use environment variable which allows
        # the use to be even more portable.
    # Falls back to 'default.db' if not set
    db_path = os.getenv('LIBRARY_DB_PATH', 'users.db')
    # Establishes a connection to the DB.
    conn = sqlite3.connect(db_path)
    # Creates a cursor object for executing SQL commands.
    cursor = conn.cursor()

    # Drops the 'users' table to start with a clean slate when server restarts.
    cursor.execute("DROP TABLE IF EXISTS users")
    # Create the 'users' table with specific columns: 'id', 'username', 'password', 'first_name', 'last_name', and 'role'.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            first_name TEXT,
            last_name TEXT,
            role TEXT
        )
    ''')

    # Drops the 'library_items' table to start with a clean slate when server restarts.
    cursor.execute("DROP TABLE IF EXISTS library_items")
    # Create the table named 'library_items' with columns for item identification (item_id), title, author, type, and availability (available).
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS library_items (
            item_id INTEGER PRIMARY KEY,
            title TEXT,
            author TEXT,
            type TEXT,
            available INTEGER DEFAULT 1
        )
    ''')

    # Drops the 'checkout' table to start with a clean slate when server restarts.
    cursor.execute("DROP TABLE IF EXISTS checkout")
    # Create the table names 'checkout' with columns: 'checkout_id', 'item_id', 'user_id'.
    # Foreign key constraints: 'item_id' references the 'item_id' column in the 'library_items' table,
        # 'user_id' references the 'id' column in the 'users' table.
    # This ensures referential integrity, meaning that only valid item IDs and user IDs can be stored in the 'checkout' table.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checkout (
            checkout_id INTEGER PRIMARY KEY,
            item_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY(item_id) REFERENCES library_items(item_id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')


    # Insert some dummy data (2 users)
    password1_hash = bcrypt.hashpw(b'pat', bcrypt.gensalt())
    password2_hash = bcrypt.hashpw(b'lib', bcrypt.gensalt())
    cursor.execute(
        "INSERT INTO users (username, password, first_name, last_name, role) VALUES (?, ?, ?, ?, ?)",
        ('Patron', password1_hash, 'Jane', 'Smith', 'Patron'))
    cursor.execute(
        "INSERT INTO users (username, password, first_name, last_name, role) VALUES (?, ?, ?, ?, ?)",
        ('Librarian', password2_hash, 'John', 'Doe', 'Librarian'))

    # Insert some dummy data (6 library_items)
    cursor.execute(
        "INSERT INTO library_items (title, author, type, available) VALUES (?, ?, ?, 1)",
        ('Book 1', 'Author 1', 'Book'))
    cursor.execute(
        "INSERT INTO library_items (title, author, type, available) VALUES (?, ?, ?, 1)",
        ('Test 2', 'Author 2', 'Book'))
    cursor.execute(
        "INSERT INTO library_items (title, author, type, available) VALUES (?, ?, ?, 1)",
        ('CD 1', 'Author 1', 'CD'))
    cursor.execute(
        "INSERT INTO library_items (title, author, type, available) VALUES (?, ?, ?, 1)",
        ('Test 2', 'Author 2', 'CD'))
    cursor.execute(
        "INSERT INTO library_items (title, author, type, available) VALUES (?, ?, ?, 1)",
        ('DVD 1', 'Author 1', 'DVD'))
    cursor.execute(
        "INSERT INTO library_items (title, author, type, available) VALUES (?, ?, ?, 1)",
        ('Test 2', 'Author 2', 'DVD'))


    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()
