#region import
from mongokit import Connection
import sys
import math
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

#region similar items
def similar_items():
  pass

def tags_to_vector(tags):
  pass

# compute cosine similarity between two vectors
# return values from <<0,1>
# good for: tags
def cosine_similarity(list1=[], list2=[]):
  if len(list1) != len(list2):
    return None

  numerator, pow1, pow2 = 0.0, 0.0, 0.0

  for i in range(0, len(list1)):
    numerator = numerator + (list1[i] * list2[i])
    pow1 = pow1 + (list1[i] * list1[i])
    pow2 = pow2 + (list2[i] * list2[i])

  denumerator = math.sqrt(pow1) * math.sqrt(pow2)
  if denumerator == 0.0:
    return 0.0
  else:
    return numerator/denumerator

# tanimoto coefficient/ jaccard index is good for
# binary representations
# good for: tags
def tanimoto_coeffiecient(list1=[],list2=[]):
  if len(list1) != len(list2):
    return None

  nc, na, nb = 0.0, 0.0, 0.0

  for i in range(0, len(list1)):
    if list1[i] == list2[i]:
      nc = nc + 1.0
    if list1[i] > 0:
      na = na + 1.0
    if list2[i] > 0:
      nb = nb + 1.0
  denumerator = na + nb - nc

  if denumerator == 0.0:
    return  0.0
  else:
    return nc/denumerator

#endregion

#region personalized
#region collaborative filtering
def collaborative_filtering():
  pass
#endregion

#region content-based
def content_based():
  pass
#endregion

#region simpeople
def similar_people():
  for user in userscol.User.find():
    sim_person(user)

def sim_person(user1):
  for user2 in userscol.User.find():
    similarity(user1, user2)

def similarity(user1, user2):
  # list of mutual ratings
  si={}
  for item in user2['ratings']:
    print item
#endregion

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
  print "5. computing similar items"
  similar_items()
  print "6. computing collaborative filtering"
  collaborative_filtering()
  print "7. computing content based recommendations"
  content_based()
  print "8. computing similar people"
  similar_people()

recommend()