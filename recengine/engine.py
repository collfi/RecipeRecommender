#region import
from operator import itemgetter
from mongokit import Connection
import sys
import math
# i need to add this because of imports
#sys.path.append('/home/michal/Desktop/RECSYS/RecipeRecommender/')
sys.path.append('/home/collfi/RecSys/RecipeRecommender/')
from sqlalchemy import and_
from webapp.models import recommender
from datetime import datetime
from math import sqrt
#endregion

#region database

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

#region precompute
def precompute_avg_userratings():
  for user in userscol.User.find():
    user['avgrating'] = average_rating_user(user)
    user.save()

def average_rating_user(user):
  average = 0.0
  if len(user['ratings']) != 0:
    for item in user['ratings']:
      average += (item['value'])
    average /= len(user['ratings'])
  return average

def precompute():
  precompute_avg_userratings()
#endregion

# Computing simple most favorite items as number of favorites
# and then save it to nonpcol document to 'topfavorites'
def most_favorite():
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
def average_ratings_recipes():
  for item in recipecol.Recipe.find():
    idrecipe = item.get('_id')
    sum = 0.0; count = 0
    # compute average for specified item
    for item1 in userscol.User.find({'ratings':{'$elemMatch':{'itemid':idrecipe}}},{'ratings.$':1}):
      sum = sum + item1.get('ratings')[0]['value']
      count = count +1
    try:
      item['avgrating'] = float(sum/float(count))
      item.save()
    except:
      #if it is exception division by zero, just skip it
      pass

# get best items from sql and save it to our
# document database.
def best_rated():
  recipes = recipecol.Recipe.find().sort('avgrating',1).limit(15)
  for item in recipes:
    recipe=nonpcol.NonPersonal.find_one({'_id':1})
    recipe['toprated'].append(int(item['_id']))
    recipe.save()

# hackernews like interested, #http://amix.dk/blog/post/19574
# compute interesting items right now by votes/favorites
def hackernews_interesting():
  interest = []
  for item in recipecol.Recipe.find():
    hours = abs(datetime.now() - item.get('date_creation')).total_seconds() / 3600.0
    item['interesting'] = hackernews_score(len(item.get('favorites')), hours)
    item.save()
    interest.append((item.get('_id'),  item['interesting']))
  interest_sorted = sorted(interest, key=lambda tup: tup[1])
  interest_sorted.reverse()
  interest_sorted = interest_sorted[:10]
  for item in interest_sorted:
    recipe = nonpcol.NonPersonal.find_one({'_id': 1})
    recipe['topinteresting'].append(int(item[0]))
    recipe.save()

def hackernews_score(votes, item_hour_age, gravity=1.8):
  return (votes + 1) / pow((item_hour_age+2), gravity)
#endregion

#region personalized
#region collaborative filtering


def collaborative_filtering():
  for u in userscol.User.find():
    pred = []

    for r in recipecol.Recipe.find():
      if u.getRating(r['_id']) is None:
        numerator = 0
        denominator = 0

        for b in u['similar_users']:
          user_b  = userscol.User.find_one({'_id': b['userid']})
          rating = user_b.getRating(r['_id'])
          if rating is None: continue

          numerator += (pearson_sim_user(u, user_b) * (rating - user_b['avgrating']))
          denominator += pearson_sim_user(u, user_b)

        if denominator == 0: continue
          #predicted_rating = u['avgrating']
          #pred.append({'itemid': r['_id'], 'value': predicted_rating})
        else:
          predicted_rating = u['avgrating'] + (numerator / denominator)
          pred.append({'itemid': r['_id'], 'value': predicted_rating})

    newlist = sorted(pred, key=itemgetter('value'), reverse=True)
    u['predicted'] = newlist[:10]
    u.save()

#Pearson Correlation Coefficient
def pearson_sim_user(user1, user2):
  if len(user1['ratings']) == 0 or len(user2['ratings']) == 0: return 0.0

  # list of mutual ratings
  mratings = []
  for item1 in user1['ratings']:
    for item2 in user2['ratings']:
      if item1['itemid'] == item2['itemid']:
        mratings.append({'itemid': item1['itemid'], 'value1': item1['value'], 'value2': item2['value']})
        continue
  # if are no common ratings
  if len(mratings) == 0: return 0.0


  #average ratings for users
  avg1 = user1['avgrating']
  avg2 = user2['avgrating']
  den1 = 0.0
  den2 = 0.0
  sum1 = 0.0
  for item in mratings:
    sum1 += ((item['value1'] - avg1) * (item['value2'] - avg2))
    den1 += (item['value1'] - avg1) ** 2
    den2 += (item['value2'] - avg2) ** 2
  den = (sqrt(den1)) * (sqrt(den2))
  if den == 0.0:
    return 0.0
  return sum1/den  #TODO: * 1/min(common items, threshold) OR just put constant in denominator

#endregion

#region content-based
def content_based():
  global G_TAGS, G_INGREDIENTS
  # 1. build user profiles
  for user in userscol.User.find():
    # 2. get favorited items and items which user ranked 4 or five
    gooditems = list(set(user['favorites'] + user.getHighlyRatedItems()))
    if len(gooditems) == 0: continue

    uservectortag = [0] * len(G_TAGS)
    useringredient = {}
    for recipeid in gooditems:
      # get the recipe
      recipe = recipecol.Recipe.find_one({'_id': recipeid})

      # compute user profile by tags
      vectortag = get_recipe_tagvector(recipe)
      uservectortag = sum_vectors(uservectortag, vectortag)

      # compute user profile by ingredients with tfidf
      for ingredient in recipe['ingredients']:
        if useringredient.get(ingredient['ingredient']):
          useringredient[ingredient['ingredient']] += 1#G_INGREDIENTS[ingredient['ingredient']]
        else:
          useringredient[ingredient['ingredient']] = 1#G_INGREDIENTS[ingredient['ingredient']]

    # final two user profiles by tags and ingredients
    userprofiletag = [value/float(len(gooditems)) for value in uservectortag]
    userprofileingredient = [{'key': key, 'value': useringredient[key]} for key in useringredient]

    print userprofiletag
    print userprofileingredient

    # 5. predicting items, cos(user,item), we can use hybrid
    sim_array = []
    for recipe in recipecol.Recipe.find():
      # if it is not already rated or faved
      if recipe['_id'] not in gooditems:
        scoretag = cossim_tag_recipe_user(userprofiletag, get_recipe_tagvector(recipe))
        scoreing = cossim_ingred_recipe_user(userprofileingredient, recipe)
        score = scoretag + scoreing
        print 'score = ', scoretag, '+', scoreing, ' =', score
        sim_array.append({'itemid':recipe['_id'], 'value':score})
    newlist = sorted(sim_array, key=itemgetter('value'), reverse = True)

    i = 0
    for item in newlist:
      user['predicted'].append({'itemid':item['itemid'], 'value':item['value']})
      user.save()
      i += 1
      if i == 7: return

#item1 is user
#item2 is recipe
def cossim_ingred_recipe_user(item1, item2):
  global G_INGREDIENTS

  # creating two vectors
  finalvector = []
  ivector1 = []
  ivector2 = []

  counting1 = 0

  for ingredient in item1:
    ivector1.append(ingredient['key'])
    counting1 += ingredient['value']
    if ingredient['key'] not in finalvector:
      finalvector.append(ingredient['key'])

  for ingredient in item2['ingredients']:
    ivector2.append(ingredient['ingredient'])
    if ingredient['ingredient'] not in finalvector:
      finalvector.append(ingredient['ingredient'])

  # compute tf-idf
  vector1 = []
  vector2 = []

  for ingredient in finalvector:
    if ingredient in ivector1: vector1.append((float(get_ingredient_value(item1,ingredient))/float(counting1))*G_INGREDIENTS[ingredient])
    else: vector1.append(0.0)
    if ingredient in ivector2: vector2.append((1.0/len(ivector2))*G_INGREDIENTS[ingredient])
    else: vector2.append(0.0)

#  print finalvector
#  print ivector1
#  print ivector2
#  print vector1
#  print vector2

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

def get_ingredient_value(item1, key):
  for ingredient in item1:
    if ingredient['key'] == key:
      return ingredient['value']
  else:
    return 0.

#
#
#
def cossim_tag_recipe_user(item1, item2):
  global G_TAGS
  if len(item1) == 0 or len(item2) == 0: return 0.0

  numerator, pow1, pow2 = 0.0, 0.0, 0.0

  for i in range(0, len(G_TAGS)):
    numerator = numerator + (item1[i] * item2[i])
    pow1 = pow1 + (item1[i] * item1[i])
    pow2 = pow2 + (item2[i] * item2[i])

  denumerator = math.sqrt(pow1) * math.sqrt(pow2)
  if denumerator == 0.0:
    return 0.0
  else:
    return numerator/denumerator

def sum_vectors(vector1,vector2):
  for i in range(0,len(vector1)):
    vector2[i] += vector1[i]
  return vector2

def get_recipe_tagvector(recipe):
  global G_TAGS
  vector = []
  for tag in G_TAGS:
    if tag in recipe['tags']:
      vector.append(1.0)
    else:
      vector.append(0.0)
  return vector
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
    sim_array.append({'userid':user2['_id'], 'value': cos_sim_user(user1, user2)})
  newlist = sorted(sim_array, key=itemgetter('value'), reverse=True)

  i = 0
  for item in newlist:
    user1['similar_users'].append({'userid': item['userid'], 'value': item['value']})
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
    item1['similar_items'].append({'itemid': item['itemid'], 'value': item['value']})
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
    if not filter(lambda simitem: simitem['itemid'] == item['itemid'], item1['similar_items']):
      item1['similar_items'].append({'itemid': item['itemid'], 'value': item['value']})
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
    count_recipes += 1
    for ingredient in recipe['ingredients']:
      if not G_INGREDIENTS.get(ingredient['ingredient']):
        G_INGREDIENTS[ingredient['ingredient']] = 1
      else:
        G_INGREDIENTS[ingredient['ingredient']] += 1
  # compute idf
  for ingredient in G_INGREDIENTS.keys():
    G_INGREDIENTS[ingredient] = math.log10(float(count_recipes) / float(G_INGREDIENTS[ingredient]))
# endregion

#endregion
#endregion

#region clean
def clear():
  pass
  # we clean some "columns" not entire document
  nonpcol.update({'_id': 1}, {'$pull': {'topfavorites':    {'$exists': True}}}, multi=True)
  nonpcol.update({'_id': 1}, {'$pull': {'toprated':        {'$exists': True}}}, multi=True)
  userscol.update({}, {'$pull': {'similar_users':          {'$exists': True}}}, multi=True)
  userscol.update({}, {'$pull': {'predicted':              {'$exists': True}}}, multi=True)
  recipecol.update({}, {'$pull': {'similar_items':         {'$exists': True}}}, multi=True)
#endregion

def recommend():
  clear()
  print "0. precompute avg.rating users"
  precompute()
  print "1. computing most favorite items"
  most_favorite()
  print "2. computing average ratings for items"
  average_ratings_recipes()
  print "3. computing best rated items"
  best_rated()
  print "4. computing interesting with hacker news formula"
  hackernews_interesting()
  print "5. computing similar people"
  similar_people()
  print "6. computing idf"
  compute_idf()
  print "7. computing similar recipes/items"
  similar_items()
  print "8. computing collaborative filtering"
  collaborative_filtering()
  print "9. computing content based recommendations by tags"
  content_based()

recommend()
