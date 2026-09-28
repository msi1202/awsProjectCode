import sqlite3
import os

DATABASE = '/home/ubuntu/flaskapp/users.db'

def create_db():
    # Ensure the directory exists
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS users")
    # Table encompasses requirements 4a, 4b, and 4e
    c.execute('''CREATE TABLE users 
                 (username TEXT PRIMARY KEY, password TEXT, firstname TEXT, 
                  lastname TEXT, email TEXT, address TEXT, filename TEXT, wordcount INTEGER)''')
    conn.commit()
    conn.close()
    print("Database and users table created successfully.")

if __name__ == '__main__':
    create_db()
