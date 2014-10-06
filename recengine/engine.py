from mongokit import Connection
from sqlalchemy import and_
from models import recommender
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
    pass

def recommend():
  print "z tejto funkcie sa budu volat vsetky funkcie na vypocty a ukladanie do db"
  mostfavorite()

recommend()