from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash
from scraper import scraper  # Ensure you have this module and it works as expected
from summarizer import summarizer, estimated_reading_time  # Ensure you have this module and it works as expected

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database configuration
DB_HOST = "localhost"
DB_NAME = "sampledb"
DB_USER = "postgres"
DB_PASS = "Vasudhap@#*?2001"
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

@app.route('/')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account and check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            flash('Incorrect username/password!')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        _hashed_password = generate_password_hash(password)

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
            conn.commit()
            flash('You have successfully registered!')

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))

# @app.route("/index", methods=['GET', 'POST'])
# def index():
#     if 'loggedin' in session:
#         # cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#         # cursor.execute("SELECT * FROM editorials")
#         # url_data = cursor.fetchone()
#         if request.method == 'POST':
#             url = request.form.get('url')
#         # if url_data:
#         #     # url_id = url_data['id']
#         #     url = url_data['url']
#             try:
#                 article_title, text = scraper(url)
#                 summary = summarizer(text)
#                 # cursor.execute("UPDATE editorials SET summary = %s WHERE ", (summary, url_data['id']))
#                 # conn.commit()
#                 reading_time = estimated_reading_time(summary.split())
#                 return render_template("index.html", article_title=article_title, reading_time=reading_time, summary=summary)
#             except TypeError:
#                 flash('Invalid URL entered')
#                 return redirect(url_for('index'))
#         else:
#             return render_template("index.html")
#     else:
#         return redirect(url_for('login'))



@app.route("/index", methods=['GET', 'POST'])
def index():
    if 'loggedin' in session:
        if request.method == 'POST':
            date = request.form.get('date')
            category = request.form.get('category')

            # Fetch rows from editorials table based on date and category
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            if category == 'all':
                cursor.execute("SELECT * FROM editorials WHERE dt = %s", (date,))
            else:
                cursor.execute("SELECT * FROM editorials WHERE dt = %s AND category = %s", (date, category))
            # cursor.execute("SELECT * FROM editorials WHERE dt = %s AND category = %s", (date, category))
            rows = cursor.fetchall()

            summaries = []
            for row in rows:
                article_title, text = scraper(row['url'])
                summary = summarizer(text)
                summaries.append({
                    'article_title': article_title,
                    'summary': summary,
                    'reading_time': estimated_reading_time(summary.split())
                })

            return render_template("index.html", summaries=summaries)

        else:
            return render_template("index.html")
    else:
        return redirect(url_for('login'))



if __name__ == "__main__":
    app.run(debug=True)
