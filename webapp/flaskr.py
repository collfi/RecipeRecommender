# The recommender system
# authors : Michal Lukac, Boris Valentovic

# all the imports
import sqlite3
from mongokit import Connection
from flask import Flask, request, session, g, redirect, url_for, render_template, flash

from models import recommender
from models.database import db_session, init_db
from models.models import User

# create our mongodb connection and register models
mconnection = Connection()
mconnection.register([recommender.User])
userscol = mconnection['recsys'].users

# create our recsys app
app = Flask(__name__)
app.config.from_object('config.Config')

# all the db functions
def connect_sqlitedb():
  return sqlite3.connect(app.config['DATABASE'])

def init_mongodb():
  recommender.init_mongodb(mconnection)

# requests
#############
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.before_request
def before_request():
  if 'logged_in' not in session and (request.endpoint != 'login' and request.endpoint != 'signup'):
    return redirect(url_for('login'))

# routing the application
############
@app.route('/')
def show_entries():
  #cur = g.db.execute('select title, text from entries order by id desc')
  #entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
  entries = None
  return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
  #g.db.execute('insert into entries (title, text) values (?, ?)',
  #  [request.form['title'], request.form['text']])
  #g.db.commit()
  flash('New entry was successfully posted')
  return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    result = User.query.filter(User.login == 'admin').first()
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
    try:
      # save to sqldb
      user = User('admin', 'admin', 'cospelthetraceur@gmail.com','admin')
      db_session.add(user)
      db_session.commit()
      # and save to nosql
      user = userscol.User()
      user['_id'] = request.form['login']
      user.save()
      return redirect(url_for('login'))
    except Exception, e:
      error = "User already exists!"
      return render_template('signup.html', error=error)
  return render_template('signup.html', error=error)

def init_route():
  # sql
  init_db()
  # mongo
  init_mongodb()

# START
if __name__ == '__main__':
  init_route()
  app.run()
