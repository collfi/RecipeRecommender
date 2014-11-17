# The recommender system: The CookBook
# authors : Michal Lukac, Boris Valentovic

from mongokit import Connection
from flask import Flask, request, session, flash, redirect, url_for, render_template, make_response
from sqlalchemy import and_, or_
from models import recommender
from datetime import datetime
import base64
import json

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
mconnection.register([recommender.Recipe])
mconnection.register([recommender.NonPersonal])

userscol = mconnection['recsys'].users
recipecol = mconnection['recsys'].recipes
nonpcol = mconnection['recsys'].nonpersonal
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
def show_entries(entries=None, headline="Recipes"):
  if entries == None:
    entries=Recipe.query.all()
  return render_template('show_entries.html', entries=entries, headline="Recipes")

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

@app.route('/user/<login>/cookbook', methods=['GET'])
def cookbook(login):
  user = userscol.User.find_one({'_id':login})
  favorites = user['favorites']
  recipes = Recipe.query.filter(or_(Recipe.userid == login, Recipe.id.in_(favorites))).all()
  return render_template('show_entries.html', entries=recipes, headline="Your cookbook")

@app.route('/user/<login>/favorites', methods=['GET'])
def user_favorites(login):
  user = userscol.User.find_one({'_id': login})
  favorites = user['favorites']
  q = db_session.query(Recipe)
  q = q.filter(Recipe.id.in_(favorites))
  entries = q.all()
  return render_template('show_profile.html', entries=entries)

#endregion

#region recipe
@app.route('/recipe/add', methods=['GET'])
def add():
  return render_template('add.html')

@app.route('/recipe/<id>/edit', methods=['GET'])
def edit(id):
  q = db_session.query(Recipe)
  q = q.filter(Recipe.id == id)
  entry = q.one()
  rec = recipecol.Recipe.find_one({'_id': int(id)})
  max = len(rec.get('ingredients'))

  if entry.userid != session['user_in']:
    return redirect(url_for('show_entries', headline="Recipes"))
  return render_template('edit.html', entry=entry, rec=rec, max=max, tags=','.join(rec['tags']))

@app.route('/recipe/add_entry', methods=['POST'])
def add_entry():
  # check the file
  file = request.files['file']
  # store the recipe
  tags = request.form['tags'].split(',')
  recipe = Recipe(None, session['user_in'], request.form['title'], request.form['text'], base64.b64encode(file.read()))
  db_session.add(recipe)
  db_session.commit()

  # create in mongo
  recipemongo = recipecol.Recipe()
  recipemongo['_id'] = recipe.id
  recipemongo['tags'] = request.form['tags'].split(',')
  recipemongo.save()
  # get ingredients
  count = 0
  nextIng = True

  #add to nonpersonal all tags
  tags = request.form['tags'].split(',')
  data = nonpcol.NonPersonal.find_one({'_id':1})

  for tag in tags:
    if tag not in data.get_tags():
      print tag
      data['tags'].append(unicode(tag))

  data.save()

  while nextIng:
    if 'ingredient_' + str(count) in request.form:
      name = request.form['ingredient_' + str(count)]
      amount =request.form['amount_' + str(count)]
      count += 1
      recipemongo['ingredients'].append({'ingredient': name, 'number': amount})

    else:
      print ("no more ingredients")
      nextIng = False
  recipemongo.save()
  flash('New entry was successfully posted')
  return redirect(url_for('show_entries', headline="Recipes"))

@app.route('/recipe/edit_entry', methods=['POST'])
def edit_entry():
  q = db_session.query(Recipe)
  q = q.filter(Recipe.id == request.form['id'])
  recipe = q.one()
  recipe.title = request.form['title']
  recipe.text = request.form['text']
  db_session.commit()
  #---------------------------------
  recipemongo = recipecol.Recipe.find_one({'_id': int(recipe.id)})
  recipemongo['tags'] = request.form['tags'].split(',')
  recipemongo['ingredients'] = []
  recipemongo.save()
  # get ingredients
  count = 0
  nextIng = True
  while nextIng:
    if 'ingredient_' + str(count) in request.form: #a sucasne aj amount!!! + aj do add() -- alebo skor osefovat ze musi zadat
      name = request.form['ingredient_' + str(count)]
      amount = request.form['amount_' + str(count)]
      count += 1
      recipemongo['ingredients'].append({'ingredient': name, 'number': amount})
    else:
      print ("no more ingredients")
      nextIng = False
  #---------------------------------
  print recipemongo['tags']
  recipemongo.save()
  return redirect(url_for('show_entries', headline="Recipes", tags=','.join(recipemongo['tags'])))

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
  canedit = None
  favorited = None

  # has user already faved the item?
  user = userscol.User.find_one({'_id': session['user_in'], 'favorites': int(id)})
  # has user already rated the idem?
  #rated  = userscol.find_one({'_id': session['user_in'], 'ratings.itemid': int(id)}, {'ratings.value': 1, '_id':1})
  rated  = userscol.find_one({'_id': session['user_in'], 'ratings.itemid': int(id)}, {'ratings.itemid': 1,
                                                                                      'ratings.value': 1, '_id': 0})
  #je to dobre? ja som myslel, ze to vybere vzdy iba jeden rating, ale ono ro vybere vsetky od uzivatela
  #a potom ich musim prechadzat vo tom for, da sa to spravit aby to vybralo iba 1 konkretny pre ten recept
  #a ja som dal nieco take ako rated.get('ratings')[0].get('value')??
  value = 0

  if rated:
    for item in rated.get('ratings'):
      if item.get('itemid') == int(id):
        value = item.get('value')

  entry = db_session.query(Recipe).get(id)
  rec = recipecol.Recipe.find_one({'_id': int(id)})
  tags = ','.join(rec['tags'])
  if user:
    favorited = True
  if entry.userid == session['user_in']:
    canedit = True
  return render_template('show_entry.html', entry=entry, canedit=canedit, favorited=favorited, value=value, rec=rec, tags=tags)
#endregion

#region recommendations
@app.route('/recommend/topfav', methods=['GET'])
def topfav():
  recipe = nonpcol.NonPersonal.find_one({'_id':1})
  q = db_session.query(Recipe)
  q = q.filter(Recipe.id.in_(recipe['topfavorites']))
  entries = q.all()
  return render_template('show_entries.html', entries=entries, headline="Top favorites")

@app.route('/recommend/toprated', methods=['GET'])
def toprated():
  recipe = nonpcol.NonPersonal.find_one({'_id':1})
  q = db_session.query(Recipe)
  q = q.filter(Recipe.id.in_(recipe['toprated']))
  entries = q.all()
  return render_template('show_entries.html', entries=entries, headline="Top rated")

@app.route('/recommend', methods=['GET'])
def recommend():
  return render_template('show_entries.html', entries=[], headline="Recommended for you")

@app.route('/interesting', methods=['GET'])
def interesting():
  recipes = Recipe.query.order_by(Recipe.interested.desc()).limit(15).all()
  return render_template('show_entries.html', entries=recipes, headline="Interesting")
#endregion
#endregion

#region api
@app.route('/api/favorite', methods=['POST'])
def favorite():
  if request.method == "POST":
    #try:
    data = json.loads(request.data)
    if data['favorite'] == '1':
      # save to users
      user = userscol.User.find_one({'_id': data['userid']})
      user['favorites'].append(int(data['itemid']))
      user.save()
      # save to recipes
      recipe = recipecol.Recipe.find_one({'_id': int(data['itemid'])})
      recipe['favorites'].append(unicode(data['userid']))
      recipe.save()
    else:
      # and remove
      mconnection['recsys'].users.update({'_id': session['user_in']},
                                         {'$pull': {'favorites': int(data['itemid'])}})
      mconnection['recsys'].recipes.update({'_id': int(data['itemid'])},
                                         {'$pull': {'favorites': data['userid']}})
    return json.dumps({'status':'OK'})

@app.route('/api/rate', methods=['POST'])
def rate():
  if request.method == "POST":
    try:
      data = json.loads(request.data)
      # insert rating for user and item
      user = userscol.User.find_one({'_id': data['userid']})
      user['ratings'].append({'itemid': data['itemid'], 'value': float(data['rating']), 'date_creation': datetime.now()})
      user.save()
      #user.print_ratings()
      return json.dumps({'status': 'OK'})
    except:
      return json.dumps({'status': 'ERR'})

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