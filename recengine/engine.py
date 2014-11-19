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

# data
G_TAGS = nonpcol.NonPersonal.find_one({'_id':1}).get('tags')

# ingredients with IDF only, not TFIDF
G_INGREDIENTS = {}
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
        sort similar user by how many common items they have #useless????????????????

        numerator = 0
        denominator = 0
        for every similar user(b)
          if item in b['ratings']
            numerator += pearson_sim_user(user, b) * (rating(b, item) - average(b))
            denominator += pearson_si_user(user, b)

        pred(user, item) = average(user) + (numerator / denominator)

        save pred to array and sort by value
        display top 5


        /******************************************
          pred(user,item) = average(u) + (sum(pearson_sim_user(u,b) * rating(b, i))) / (sum(pearson_sim_user(u,b)))

        OR

        //WRONG!
        for every similar user(b)
          sum_pearson += pearson_sim_user(user, b)
        pred(user, item) = average(user) + (sum_pearson * rating(b, item)) / (sum_pearson)

        OR

        as previous, but that for cycle to the first cycle!*/
        ********************************************/

  .what if they have only few similar items?
  .in similarity, pick only similar, not exactly 7 every time - pick those, with similarity > 0.7, maximum 7 (20-30)

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
        break

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
  return (sum1)/((sqrt(den1))*(sqrt(den2))) # * 1/min(common items, treshold) OR just put constant in denominator

#endregion

#region content-based
def content_based_tags():
  # 1. build user profiles
  for user in userscol.User.find():
    # 2. get favorited items
    favitems = user.get('favorites')
    # 3. and build user profiles by tags and ingredients
    for item in favitems:
      vector = get_recipe_tagvector()
    # 4. you can get also rated items
    #    and build weighted user profiles by tags and ingredients
  # 5. predicting items, cos(user,item)
  pass

def content_based_ingredients():
  pass

def get_recipe_tagvector():
  return None
#endregion

#region similar people
# we compute for each user 7 most similar people
def similar_people():
  for user in userscol.User.find():
    sim_person(user)

def sim_person(user1):
  sim_array = []
  for user2 in userscol.User.find():
    if user1['_id'] == user2['_id']: continue
    sim_array.append({'userid':user2['_id'], 'value':cos_sim_user(user1,user2)})
  newlist = sorted(sim_array, key=itemgetter('value'), reverse = True)

  i = 0
  for item in newlist:
    user1['similiar_users'].append({'userid':item['userid'],'value':item['value']})
    user1.save()
    i += 1
    if i == 7: return

# this is cosine similarity between two users based on ratings
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
    sim_item_tags(item1)
    sim_item_ingredients(item1)
    #print('-----')

# compute similiar items for item through tag
def sim_item_tags(item1):
  sim_array = []
  for item2 in recipecol.Recipe.find():
    if item2['_id'] == item1['_id']: continue
    sim_array.append({'itemid':item2['_id'], 'value': cos_sim_recipes_tags(item1, item2)})
  newlist = sorted(sim_array, key=itemgetter('value'), reverse = True)

  i = 0
  for item in newlist:
    item1['similiar_items'].append({'itemid': item['itemid'], 'value': item['value']})
    item1.save()
    i += 1
    if i == 5: return

# compute similiar items for item through the tf-idf with ingredients
def sim_item_ingredients(item1):
  sim_array = []
  for item2 in recipecol.Recipe.find():
    if item2['_id'] == item1['_id']: continue
    sim_array.append({'itemid':item2['_id'], 'value': cos_sim_recipes_ingredients(item1, item2)})
  newlist = sorted(sim_array, key=itemgetter('value'), reverse = True)

  i = 0
  for item in newlist:
    # if the item was not previously added through tag similarity
    if not filter(lambda simitem: simitem['itemid'] == item['itemid'], item1['similiar_items']):
      item1['similiar_items'].append({'itemid': item['itemid'], 'value': item['value']})
      item1.save()
      i += 1
    if i == 5: return


# cos sim between two recipes based on ingredients
# the vector space model is based on tf-idf
#           x.y
# cos  = ---------
#         |x|.|y|
def cos_sim_recipes_ingredients(item1, item2):
  global G_INGREDIENTS
  if item1['_id'] == item2['_id']: return 0.0
  if len(item1['tags']) == 0 or len(item2['tags']) == 0: return 0.0

  # creating two vectors
  finalvector = []
  ivector1 = []
  ivector2 = []
  for ingredient in item1['ingredients']:
    ivector1.append(ingredient['ingredient'])
    if ingredient['ingredient'] not in finalvector:
      finalvector.append(ingredient['ingredient'])

  for ingredient in item2['ingredients']:
    ivector2.append(ingredient['ingredient'])
    if ingredient['ingredient'] not in finalvector:
      finalvector.append(ingredient['ingredient'])

  # compute tf-idf
  vector1 = []
  vector2 = []
  for ingredient in finalvector:
    if ingredient in ivector1: vector1.append((1.0/len(ivector1))*G_INGREDIENTS[ingredient])
    else: vector1.append(0.0)
    if ingredient in ivector2: vector2.append((1.0/len(ivector2))*G_INGREDIENTS[ingredient])
    else: vector2.append(0.0)

  # and now compute cosine similarity
  numerator, pow1, pow2 = 0.0, 0.0, 0.0
  for i in range(0,len(finalvector)):
    numerator = numerator + (vector1[i] * vector2[i])
    pow1 = pow1 + (vector1[i] * vector1[i])
    pow2 = pow2 + (vector2[i] * vector2[i])

  denumerator = math.sqrt(pow1) * math.sqrt(pow2)
  if denumerator == 0.0:
    return 0.0
  else:
    return numerator/denumerator

# cos sim between two recipes based on tags
#           x.y
# cos  = ---------
#         |x|.|y|
def cos_sim_recipes_tags(item1, item2):
  global G_TAGS
  if item1['_id'] == item2['_id']: return 0.0
  if len(item1['tags']) == 0 or len(item2['tags']) == 0: return 0.0

  vector1 = []
  vector2 = []

  for tag in G_TAGS:
    #print tag
    if tag in item1['tags']: vector1.append(1.0)
    else: vector1.append(0.0)
    if tag in item2['tags']: vector2.append(1.0)
    else: vector2.append(0.0)
  #print vector1
  numerator, pow1, pow2 = 0.0, 0.0, 0.0

  for i in range(0, len(G_TAGS)):
    numerator = numerator + (vector1[i] * vector2[i])
    pow1 = pow1 + (vector1[i] * vector1[i])
    pow2 = pow2 + (vector2[i] * vector2[i])

  denumerator = math.sqrt(pow1) * math.sqrt(pow2)
  if denumerator == 0.0:
    return 0.0
  else:
    return numerator/denumerator

#endregion

# region idf
# compute idf for all ingredients in recipes
# and save it to global variable G_INGREDIENTS
# then we can use the idf later
def compute_idf():
  global G_INGREDIENTS
  G_INGREDIENTS = {}
  count_recipes = 0
  # get all ingredients
  for recipe in recipecol.Recipe.find():
    count_recipes = count_recipes + 1
    for ingredient in recipe['ingredients']:
      if not G_INGREDIENTS.get(ingredient['ingredient']):
        G_INGREDIENTS[ingredient['ingredient']] = 1
      else:
        G_INGREDIENTS[ingredient['ingredient']] = G_INGREDIENTS[ingredient['ingredient']] + 1
  # compute idf
  for ingredient in G_INGREDIENTS.keys():
    #print 'computing ', ingredient, 'log(',count_recipes,'/',ingredients[ingredient],')'
    G_INGREDIENTS[ingredient]  = math.log10(float(count_recipes) / float(G_INGREDIENTS[ingredient]))
    #print ingredient,':',ingredients[ingredient]
# endregion

#endregion
#endregion

#region clean
def clear():
  pass
  # we clean some "columns" not entire document
  nonpcol.update({'_id': 1}, {'$pull': {'topfavorites':    {'$exists': True}}}, multi=True)
  nonpcol.update({'_id': 1}, {'$pull': {'toprated':        {'$exists': True}}}, multi=True)
  userscol.update( {}, {'$pull': {'similiar_users':  {'$exists': True}}}, multi=True)
  recipecol.update({}, {'$pull': {'similiar_items':  {'$exists': True}}}, multi=True)
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
  print "6. computing idf"
  compute_idf()
  print "7. computing similar recipes/items"
  similar_items()
  print "8. computing content based recommendations by tags"
  content_based_tags()
  print "9. computing conent based recommendations byt ingredients"
  content_based_ingredients()
  print "10. computing collaborative filtering"
  collaborative_filtering()

recommend()
