from mongokit import Connection
import sys
# i need to add this because of imports
#sys.path.append('/home/michal/Desktop/recsys/RecipeRecommender/')
sys.path.append('/home/collfi/RecSys/RecipeRecommender/')
from sqlalchemy import and_
from webapp.models import recommender
from datetime import datetime
import base64
import json

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

def mostfavorite():
  fav = []
  for item in recipecol.Recipe.find():
    #fav[item.get('_id')] = len(item.get('favorites'))
    fav.append((item.get('_id'),  len(item.get('favorites'))))
  fav_sorted = sorted(fav, key=lambda tup: tup[1])
  fav_sorted.reverse()
  fav_sorted = fav_sorted[:5]
  #alebo fav_sorted = fav_sorted.reverse()[:5]??
  for item in fav_sorted:
    recipe = nonpcol.NonPersonal.find()
    recipe['top5favorites'].append(int(item[0]))
    recipe.save()

def recommend():
  print "z tejto funkcie sa budu volat vsetky funkcie na vypocty a ukladanie do db"
  mostfavorite()

recommend()