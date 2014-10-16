#region import
from mongokit import Connection
import sys
# i need to add this because of imports
sys.path.append('/home/michal/Desktop/RECSYS/RecipeRecommender/')
#sys.path.append('/home/collfi/RecSys/RecipeRecommender/')
from sqlalchemy import and_
from webapp.models import recommender
from datetime import datetime
#endregion

#region database
# this is our sqlalchemy orm which works with our
# simple sqlite database to store basic data
from webapp.models.database import db_session, init_db
from webapp.models.models import User, Recipe

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

#region computing
#region nonpersonalized

# Computing simple most favorite items as number of favorites
# and then save it to nonpcol document to 'topfavorites'
def mostfavorite():
  fav = []
  for item in recipecol.Recipe.find():
    #fav[item.get('_id')] = len(item.get('favorites'))
    fav.append((item.get('_id'),  len(item.get('favorites'))))
  fav_sorted = sorted(fav, key=lambda tup: tup[1])
  fav_sorted.reverse()
  fav_sorted = fav_sorted[:10]
  #alebo fav_sorted = fav_sorted.reverse()[:5]??
  nonpcol.drop()
  nonitem = nonpcol.NonPersonal()
  nonitem['_id'] = 1
  nonitem.save()
  for item in fav_sorted:
    recipe = nonpcol.NonPersonal.find_one({'_id': 1})
    recipe['topfavorites'].append(int(item[0]))
    recipe.save()

# Computing average ratings for every recipe
# and then save it to sql database to recipe
# this function precomputes average ratings for bestrated function
def averagerating():
  fav = []
  for item in recipecol.Recipe.find():
    idrecipe = item.get('_id')
    sum = 0.0; count = 0
    # compute average for specified item
    for item in userscol.User.find({'ratings':{'$elemMatch':{'itemid':idrecipe}}},{'ratings.$':1}):
      sum = sum + item.get('ratings')[0]['value']
      count = count +1
    try:
      average = float(sum/float(count))
      # and now save to db
      # find the item in our sqldb and update and save it
      q = db_session.query(Recipe).filter(Recipe.id == idrecipe)
      recipe = q.one()
      recipe.avgrating = average
      db_session.commit()
    except:
      #if it is exception division by zero, just skip it
      pass

# get best items from sql and save it to our
# document database.
def bestrated():
  recipes = Recipe.query.order_by(Recipe.avgrating.desc()).limit(15).all()
  for item in recipes:
    recipe=nonpcol.NonPersonal.find_one({'_id':1})
    recipe['toprated'].append(int(item.id))
    recipe.save()

# hackernews like interested, #http://amix.dk/blog/post/19574
# compute interesting items right now by votes/favorites
def hackernews_interesting():
  for item in recipecol.Recipe.find():
    hours = abs(datetime.now() - item.get('date_creation')).total_seconds() / 3600.0
    score = hackernews_score(len(item.get('favorites')), hours)
    q = db_session.query(Recipe).filter(Recipe.id == item.get('_id'))
    recipe = q.one()
    recipe.interested = score

def hackernews_score(votes, item_hour_age, gravity=1.8):
  return (votes + 1) / pow((item_hour_age+2), gravity)
#endregion

#endregion

def recommend():
  print "1. computing most favorite items"
  mostfavorite()
  print "2. computing average ratings for items"
  averagerating()
  print "3. computing best rated items"
  bestrated()
  print "4. computing interesting with hacker news formula"
  hackernews_interesting()

recommend()