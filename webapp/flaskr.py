# The recommender system: The CookBook
# authors : Michal Lukac, Boris Valentovic

from mongokit import Connection
from flask import Flask, request, session, flash, redirect, url_for, render_template, make_response
from sqlalchemy import and_
from models import recommender
import base64

#region database
# this is our sqlalchemy orm which works with our
# simple sqlite database to store basic data
from models.database import db_session, init_db
from models.models import User, Recipe

# constants
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# create our mongodb connection and register models
# this is our recommender computing database
mconnection = Connection()
mconnection.register([recommender.User])
userscol = mconnection['recsys'].users
#endregion

# create our recsys app
app = Flask(__name__)
app.config.from_object('config.Config')

#region misc
def init_mongodb():
  recommender.init_mongodb(mconnection)

def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
#endregion

# region requests
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.before_request
def before_request():
  if 'logged_in' not in session and (request.endpoint != 'login' and request.endpoint != 'signup'):
    return redirect(url_for('login'))
#endregion

#region routing
@app.route('/', methods=['GET'])
def show_entries():
  return render_template('show_entries.html', entries=Recipe.query.all())

#region user
@app.route('/user/<login>', methods=['GET', 'POST'])
def show_profile(login):
  return render_template('show_profile.html', user=db_session.query(User).get(login))

@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    user = User.query.filter(and_(User.login == request.form['login'], User.password == request.form['password'])).first()
    if user:
      session['logged_in'] = True
      session['user_in'] = request.form['login']
      flash('You were logged in as ' + request.form['login'])
      return redirect(url_for('show_entries'))
    else:
      error = 'Invalid username or password'
  return render_template('login.html', error=error)

@app.route('/logout')
def logout():
  session.pop('logged_in', None)
  session.pop('user_in', None)
  flash('You were logged out')
  return redirect(url_for('show_entries'))

@app.route('/signup', methods=['GET','POST'])
def signup():
  error = None
  if request.method == 'POST':
    try:
      # save to sqldb
      user = User(request.form['login'], request.form['fullname'], request.form['email'], request.form['password'])
      db_session.add(user)
      db_session.commit()
      # and save document to mongodb
      user = userscol.User()
      user['_id'] = request.form['login']
      user.save()
      return redirect(url_for('login'))
    except Exception, e:
      error = "User already exists!"
      return render_template('signup.html', error=error)
  return render_template('signup.html', error=error)
#endregion

#region recipe
@app.route('/recipe/add', methods=['GET'])
def add():
  return render_template('add.html')

@app.route('/recipe/<id>/edit', methods=['GET'])
def edit(id):
  q = db_session.query(Recipe)
  q = q.filter(Recipe.id == id)
  record = q.one()
  return render_template('edit.html', entry=record)

@app.route('/recipe/add_entry', methods=['POST'])
def add_entry():
  # check the file
  file = request.files['file']
  # store the recipe
  recipe = Recipe(None, session['user_in'], request.form['title'], request.form['text'], request.form['tags'],
                  base64.b64encode(file.read()))
  db_session.add(recipe)
  db_session.commit()
  flash('New entry was successfully posted')
  return redirect(url_for('show_entries'))

@app.route('/recipe/edit_entry', methods=['POST'])
def edit_entry():
  q = db_session.query(Recipe)
  q = q.filter(Recipe.id == request.form['id'])
  recipe = q.one()
  recipe.title = request.form['title']
  recipe.text = request.form['text']
  recipe.tags = request.form['tags']
  db_session.commit()
  return redirect(url_for('show_entries'))

@app.route("/recipe/<id>.png")
def image(id):
  q = db_session.query(Recipe)
  q = q.filter(Recipe.id == id)
  recipe = q.one()
  response = make_response(recipe.image)
  response.headers['Content-Type'] = 'image/jpeg'
  response.headers['Content-Disposition'] = 'attachment; filename=img.jpg'
  return response

@app.route('/recipe/<id>', methods=['GET', 'POST'])
def show_entry(id):
  return render_template('show_entry.html', entry=db_session.query(Recipe).get(id))
#endregion
#endregion

def init_route():
  # sqlalchemy
  init_db()
  # mongo
  init_mongodb()

# START
if __name__ == '__main__':
  init_route()
  app.run()