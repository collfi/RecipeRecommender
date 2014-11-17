#region import
from operator import itemgetter
from mongokit import Connection
import sys
import math
# i need to add this because of imports
sys.path.append('/home/michal/Desktop/RECSYS/RecipeRecommender/')
#sys.path.append('/home/collfi/RecSys/RecipeRecommender/')
from sqlalchemy import and_
from webapp.models import recommender
from datetime import datetime
from math import sqrt
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

#region personalized
#region collaborative filtering
def collaborative_filtering():
  '''
  for every user
    for every item
      if not in user['ratings']
        sort similar user by how many common items they have

          pred(user,item) = average(u) + (sum(pearson_sim_user(u,b) * rating(b, i))) / (sum(pearson_sim_user(u,b)))

        OR

        for every similar user(b)
          sum_pearson += pearson_sim_user(user, b)
        pred(user, item) = average(user) + (sum_pearson * rating(b, item)) / (sum_pearson)

        OR

        as previous, but that for cycle to the first cycle!

      save pred to array and sort by value
      display top 5

  .what if they have only few similar items?
  .in similarity, pick only similar, not exactly 7 every time

  '''
  pass

#Pearson Correlation Coefficient
def pearson_sim_user(user1, user2):
  if user1['_id'] == user2['_id']: return 0.0 # should be 1.0 but we don't want to compute this
  if len(user1['ratings']) == 0 or len(user2['ratings']) == 0: return 0.0

  # list of mutual ratings
  mratings = []
  for item1 in user1['ratings']:
    for item2 in user2['ratings']:
      if item1['itemid'] == item2['itemid']:
        mratings.append({'itemid': item1['itemid'], 'value1': item1['value'], 'value2': item2['value']})
        break #???????????????????????????/

  # if are no common ratings
  if len(mratings) == 0: return 0.0


  #average ratings for users
  average1 = 0
  for item in user1['ratings']:
    average1 += (item['value'])
  average1 /= len(user1['ratings'])
  average2 = 0
  for item in user2['ratings']:
    average2 += (item['value'])
  average2 /= len(user2['ratings'])

  den1 = 0
  den2 = 0
  sum1 = 0
  for item in mratings:
    sum1 += ((item.get('value1') - average1) * (item.get('value2') - average2))
    den1 += (item.get('value1') - average1) * (item.get('value1') - average1)
    den2 += (item.get('value2') - average2) * (item.get('value2') - average2)
  return (sum1)/((sqrt(den1))*(sqrt(den2)))

#endregion

#region content-based
def content_based():
  # 1. compute item vectors
  # 2. build user profiles
  # 3. predicting items, cos(user,item)
  pass
#endregion

#region similar people
# we compute for each user 7 most similar people
def similar_people():
  for user in userscol.User.find():
    sim_person(user)

def sim_person(user1):
  sim_array = []
  for user2 in userscol.User.find():
    sim_array.append({'userid':user2['_id'], 'value':cos_sim_user(user1,user2)})
  newlist = sorted(sim_array, key=itemgetter('value'), reverse = True)

  i = 0
  for item in newlist:
    user1['similiar_users'].append({'userid':item['userid'],'value':item['value']})
    user1.save()
    i += 1
    if i == 7: return
# this is cosine similarity between two users
#           x.y
# cos  = ---------
#         |x|.|y|
def cos_sim_user(user1, user2):
  if user1['_id'] == user2['_id']: return 0.0 # should be 1.0 but we don't want to compute this
  if len(user1['ratings']) == 0 or len(user2['ratings']) == 0: return 0.0

  # list of mutual ratings
  mratings = []
  for item1 in user1['ratings']:
    for item2 in user2['ratings']:
      if item1['itemid'] == item2['itemid']:
        mratings.append(item1['itemid'])

  # if are no common ratings
  if len(mratings) == 0: return 0.0

  numerator, pow1, pow2 = 0.0, 0.0, 0.0

  for item in user1['ratings']:
    pow1 = pow1 + (item['value'] * item['value'])

  for item in user2['ratings']:
    pow2 = pow2 + (item['value'] * item['value'])

  denumerator = math.sqrt(pow1) * math.sqrt(pow2)

  if denumerator == 0.0: return 0.0

  for itemid in mratings:
    rating1 = user1.getRating(itemid)
    rating2 = user2.getRating(itemid)
    numerator = numerator + (rating1 * rating2)

  return numerator/denumerator


#endregion

#region similar items
def similar_items():
  for item1 in recipecol.Recipe.find():
    for item2 in recipecol.Recipe.find():
      print cos_sim_recipes(item1, item2)

def cos_sim_recipes(item1, item2):
  recipe=nonpcol.NonPersonal.find_one({'_id':1})
  tags = recipe.get_tags()
  vector1, vector2 = [], []

  print tags
  for tag in tags:
    if tag in item1['tags']: vector1.append(1.0)
    else: vector1.append(0.0)
    if tag in item2['tags']: vector2.append(1.0)
    else: vector2.append(0.0)

  numerator, pow1, pow2 = 0.0, 0.0, 0.0

  for i in range(0, len(tags)):
    numerator = numerator + (vector1[i] * vector2[i])
    pow1 = pow1 + (vector1[i] * vector1[i])
    pow2 = pow2 + (vector2[i] * vector2[i])

  denumerator = math.sqrt(pow1) * math.sqrt(pow2)
  if denumerator == 0.0:
    return 0.0
  else:
    return numerator/denumerator

#endregion
#endregion
#endregion

#region clean
def clear():
  nonpcol.drop()
  userscol.update({}, {'$pull': {'similiar_users': {'$exists': True}} }, multi=True)
#endregion

def recommend():
  clear()
  print "1. computing most favorite items"
  mostfavorite()
  print "2. computing average ratings for items"
  averagerating()
  print "3. computing best rated items"
  bestrated()
  print "4. computing interesting with hacker news formula"
  hackernews_interesting()
  print "5. computing similar people"
  similar_people()
  print "6. computing similar recipes/items"
  similar_items()
  print "7. computing content based recommendations"
  content_based()
  print "8. computing collaborative filtering"
  collaborative_filtering()

recommend()