# The recommender system: The CookBook
# authors : Michal Lukac, Boris Valentovic

from mongokit import Connection
from flask import Flask, request, session, flash, redirect, url_for, render_template, make_response
from sqlalchemy import and_, or_
from models import recommender
from datetime import datetime
import base64
import json
import re

#region database
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
  recommender.init_mongodbnew(mconnection)

def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
#endregion

# region requests
@app.before_request
def before_request():
  if 'logged_in' not in session and (request.endpoint != 'login' and request.endpoint != 'signup'):
    return redirect(url_for('login'))
#endregion

#region routing
@app.route('/', methods=['GET'])
def show_entries(entries=None, headline="Recipes"):
  if entries == None:
    entries=recipecol.Recipe.find()
  return render_template('show_entries.html', entries=entries, headline="Recipes")

#region user
@app.route('/user/<login>', methods=['GET', 'POST'])
def show_profile(login):
  user = userscol.User.find_one({'_id': login})
  simpeople_ids = user['similar_users']
  simpeople = []
  i = 0
  for user_id in simpeople_ids:
    simpeople.append(user_id['userid'])
    i += 1
    if i == 3: break
    #simpeople.append(userscol.User.find_one({'_id': user_id['userid']}))

  #for user_id in simpeople_ids:
  #  if user_id['value'] > 0.7: #TODO pick the most similar only! + delete print
  #    simpeople.append(userscol.User.find_one({'_id': user_id['userid']}))
  return render_template('show_profile.html', user=userscol.User.find_one({'_id': login}), simpeople=simpeople)

@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    user = userscol.User.find_one({'_id': request.form['login'], 'password':request.form['password']})
    print user
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
      # save document to mongodb
      user = userscol.User()
      user['_id'] = request.form['login']
      user['fullname'] = request.form['fullname']
      user['email'] = request.form['email']
      user['password'] = request.form['password']
      user.save()
      return redirect(url_for('login'))
    except Exception, e:
      error = "User already exists!"
      return render_template('signup.html', error=error)
  return render_template('signup.html', error=error)

@app.route('/user/<login>/cookbook', methods=['GET'])
def cookbook(login):
  user = userscol.User.find_one({'_id':login})
  recipes = recipecol.Recipe.find({'$or': [{'userid': login}, {'_id':{'$in':user['favorites']}}]})
  headline = login + '\'s Cookbook'
  return render_template('show_entries.html', entries=recipes, headline=headline)

@app.route('/user/<login>/favorites', methods=['GET'])
def user_favorites(login):
  user = userscol.User.find_one({'_id': login})
  recipes = recipecol.Recipe.find({'id': {'$in': user['favorites']}})
  return render_template('show_profile.html', entries=recipes)

#endregion

#region recipe
@app.route('/recipe/add', methods=['GET'])
def add():
  return render_template('add.html')

@app.route('/recipe/<id>/edit', methods=['GET'])
def edit(id):
  entry = recipecol.Recipe.find_one({'_id': id})
  rec = recipecol.Recipe.find_one({'_id': int(id)})
  max = len(rec.get('ingredients'))

  if entry.userid != session['user_in']:
    return redirect(url_for('show_entries', headline="Recipes"))
  return render_template('edit.html', entry=entry, rec=rec, max=max, tags=','.join(rec['tags']))

@app.route('/recipe/add_entry', methods=['POST'])
def add_entry():
  # check the image file
  #file = request.files['file']

  # store the recipe
  tags = request.form['tags'].split(',')

  # create in mongo
  recipemongo = recipecol.Recipe()
  #recipemongo['_id'] = recipe.id
  recipemongo['userid'] = session['user_in']
  recipemongo['title'] = request.form['title']
  recipemongo['text'] = request.form['text']
  recipemongo['tags'] = tags
  recipemongo.save()

  # get ingredients
  count = 0
  nextIng = True

  #add to nonpersonal all tags
  data = nonpcol.NonPersonal.find_one({'_id':1})

  for tag in tags:
    if tag not in data.get('tags'):
      data['tags'].append(unicode(tag))
  data.save()

  # and ingredients
  while nextIng:
    if 'ingredient_' + str(count) in request.form:
      name = request.form['ingredient_' + str(count)]
      amount = request.form['amount_' + str(count)]
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
  recipemongo = recipecol.Recipe.find_one({'_id': int(request.form['id'])})
  recipemongo['tags'] = request.form['tags'].split(',')
  recipemongo['title'] = request.form['title']
  recipemongo['text'] = request.form['text']
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
  recipemongo.save()
  return redirect(url_for('show_entries', headline="Recipes", tags=','.join(recipemongo['tags'])))

@app.route("/recipe/<id>.png")
def image(id):
#  q = db_session.query(Recipe)
#  q = q.filter(Recipe.id == id)
#  recipe = q.one()
#  response = make_response(recipe.image)
#  response.headers['Content-Type'] = 'image/jpeg'
#  response.headers['Content-Disposition'] = 'attachment; filename=img.jpg'
  return None#response


@app.route('/search/<text>', methods=['GET'])
def search(text=None):
  entries=recipecol.Recipe.find({'title': {'$regex': re.compile(text, re.IGNORECASE)}})
  return render_template('show_entries.html', entries=entries, headline="Recipes like " + text)

@app.route('/recipe/<id>', methods=['GET', 'POST'])
def show_entry(id):
  canedit = None
  favorited = None

  # has user already faved the item?
  user = userscol.User.find_one({'_id': session['user_in'], 'favorites': int(id)})
  rated  = userscol.User.find_one({'_id': session['user_in'], 'ratings.itemid': int(id)}, {'ratings.itemid': 1,
                                                                           'ratings.value': 1, '_id': 0})
  value = 0
  if rated:
    for item in rated.get('ratings'):
      if item.get('itemid') == int(id):
        value = item.get('value')

  # get tags
  rec = recipecol.Recipe.find_one({'_id': int(id)})
  tags = ','.join(rec['tags'])

  # now show similar recipes
  simrecipes_ids = rec['similar_items']
  simrecipes_t = []
  simrecipes_i = []
  for recipe_ in simrecipes_ids:
    if recipe_['type'] == 1:
      simrecipes_t.append(recipecol.Recipe.find_one({'_id':recipe_['itemid']}))
    else:
      simrecipes_i.append(recipecol.Recipe.find_one({'_id':recipe_['itemid']}))

  # if is users logged in recipe then he can edit it
  if user:
    favorited = True
  if rec['userid'] == session['user_in']:
    canedit = True
  return render_template('show_entry.html', canedit=canedit, favorited=favorited, value=value, rec=rec, tags=tags, simrecipes_t=simrecipes_t, simrecipes_i=simrecipes_i)
#endregion

#region recommendations
@app.route('/recommend/topfav', methods=['GET'])
def topfav():
  recipe = nonpcol.NonPersonal.find_one({'_id':1})
  entries = recipecol.Recipe.find({'_id': {'$in': recipe['topfavorites']}})
  if entries == None: entries = []
  return render_template('show_entries.html', entries=entries, headline="Top favorites")

@app.route('/recommend/toprated', methods=['GET'])
def toprated():
  recipe = nonpcol.NonPersonal.find_one({'_id':1})
  entries = recipecol.Recipe.find({'_id': {'$in': recipe['toprated']}})
  print entries
  if entries == None: entries = []
  return render_template('show_entries.html', entries=entries, headline="Top rated")

@app.route('/user/<login>/recommend', methods=['GET'])
def recommend(login):
  user = userscol.User.find_one({'_id':login})
  values = [predict['itemid'] for predict in user['predicted']]
  entries = recipecol.Recipe.find({'_id': {'$in': values}})
  if entries == None: entries = []
  return render_template('show_entries.html', entries=entries, headline="Recommended for you")

@app.route('/interesting', methods=['GET'])
def interesting():
  recipe = nonpcol.NonPersonal.find_one({'_id': 1})
  entries = recipecol.Recipe.find({'_id': {'$in': recipe['topinteresting']}})
  if entries == None: entries = []
  return render_template('show_entries.html', entries=entries, headline="Interesting")
#endregion

#region recipes-tags
@app.route('/recipes/<type>/<value>', methods=['GET'])
def show_recipes_adv(type=None,value=None, headline="Recipes"):
  if type == 'tags': # tags
    entries=recipecol.Recipe.find({'tags':{'$in':[value]}})
    return render_template('show_entries.html', entries=entries, headline="Recipes in " + value)
  else:         # ingredients
    entries=recipecol.Recipe.find({'ingredients.ingredient':{'$in':[value]}})
    return render_template('show_entries.html', entries=entries, headline="Recipes in " + value)
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
  # mongo
  init_mongodb()

# START
if __name__ == '__main__':
  init_route()
  app.run()