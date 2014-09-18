# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'dev key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our recsys app
app = Flask(__name__)
app.config.from_object(__name__)

# db
############
def connect_db():
  return sqlite3.connect(app.config['DATABASE'])

def init_db():
  with closing(connect_db()) as db:
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

@app.before_request
def before_request():
  g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()

# misc functions
############
def check_session():
  if not session.get('logged_in'):
    abort(401)

# routing the application
############
@app.route('/')
def show_entries():
  cur = g.db.execute('select title, text from entries order by id desc')
  entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
  return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
  check_session()
  g.db.execute('insert into entries (title, text) values (?, ?)',
    [request.form['title'], request.form['text']])
  g.db.commit()
  flash('New entry was successfully posted')
  return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    cur = g.db.execute("select * from users where login = '{0}' and password = '{1}'".format(request.form['login'],request.form['password']))
    result = cur.fetchone()
    if result:
      session['logged_in'] = True
      flash('You were logged in')
      return redirect(url_for('show_entries'))
    else:
      error = 'Invalid username or password'
  return render_template('login.html', error=error)

@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  flash('You were logged out')
  return redirect(url_for('show_entries'))

@app.route('/signup', methods=['GET','POST'])
def signup():
  error = None
  if request.method == 'POST':
    g.db.execute("insert into users (login, fullname, email, password) VALUES ('{0}', '{1}', '{2}', '{3}')".format(
      request.form['login'],request.form['fullname'],request.form['email'],request.form['password']))
    g.db.commit()
    return redirect(url_for('login'))
  return render_template('signup.html', error=error)

def init_route():
  pass

# START
if __name__ == '__main__':
  init_db()
  init_route()
  app.run()
