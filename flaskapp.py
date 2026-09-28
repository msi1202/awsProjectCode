import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, g

app = Flask(__name__)

# Absolute paths for mod_wsgi environment
BASE_DIR = '/home/ubuntu/flaskapp'
app.config['DATABASE'] = os.path.join(BASE_DIR, 'users.db')
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Database Connection Management (From Tutorial) ---
def connect_to_database():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def execute_query(query, args=()):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows
# ----------------------------------------------------

@app.route('/')
def index():
    # 4d: Initial entry point / re-login page
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    rows = execute_query("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    
    if rows:
        return redirect(url_for('profile', username=username))
    return "Invalid credentials. <a href='/'>Try again</a>"

@app.route('/register_page')
def register_page():
    # 4a & 4b: Registration page
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    # Accept basic user details
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    address = request.form['address']
    
    # 4e: Handle file upload and calculate word count
    file = request.files.get('limerick_file')
    filename = ""
    wordcount = 0
    
    if file and file.filename:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            wordcount = len(content.split())
            
    # Insert into database
    db = get_db()
    try:
        db.execute("INSERT INTO users (username, password, firstname, lastname, email, address, filename, wordcount) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (username, password, firstname, lastname, email, address, filename, wordcount))
        db.commit()
    except sqlite3.IntegrityError:
        return "Username already exists. <a href='/register_page'>Try again</a>"
    
    # 4c: Redirect to display page upon submission
    return redirect(url_for('profile', username=username))

@app.route('/profile/<username>')
def profile(username):
    # Retrieve user information
    rows = execute_query("SELECT * FROM users WHERE username=?", (username,))
    
    if rows:
        return render_template('profile.html', user=rows[0])
    return "User not found."

@app.route('/download/<filename>')
def download_file(filename):
    # Route for the file download button
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
