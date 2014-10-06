from mongokit import Connection, Document
from datetime import datetime

def max_length(length):
  def validate(value):
    if len(value) <= length:
      return True
    raise Exception('String in mongodb must be at most ' + length + ' chacters long!')
  return validate

class User(Document):
  structure = {
    #'_id' : str,
    #_id is login, every object in mongodb has _id attribute

    # value is rating, itemid is id of item
    'ratings' : [{'itemid' : int, 'value' : float, 'date_creation' : datetime}],
    # these are ids of recipes
    'favorites' : [ int],
  }
  use_dot_notation = True
  #required_fields = ['_id']
  #default_values = {...}
  def print_ratings(self):
    print "ratings:", self.ratings

  def print_favorites(self):
    print "favorites:", self.favorites

  def __repr__(self):
    return '<User %r>' % (self._id)

class Recipe(Document):
  structure = {
    # _id is id of recipe
    #favorites is list of user ids
    'favorites' : [ unicode ],
  }
  use_dot_notation = True
  def print_favorites(self):
    print "favorites:", self.favorites

  def __repr__(self):
    return '<Recipe %r>' % (self._id)


class NonPersonal(Document):
  structure = {
      # ids of top5favorites recipes
      'top5favorites' : [ int]
  }
  use_dot_notation = True

  def print_top5favorites(self):
      print "top 5 favorites:", self.top5favorites

  def __repr__(self):
    return '<NonPersonal %r>' % (self._id)


def init_mongodb(mconnection):
  userscol = mconnection['recsys'].users
  userscol.drop()
  recipecol = mconnection['recsys'].recipes
  recipecol.drop()
  nonpcol = mconnection['recsys'].nonpersonal
  nonpcol.drop()
  recipe = recipecol.Recipe()
  recipe['_id'] = 1
  recipe.save()
  user = userscol.User()
  user['_id'] = 'admin'
  user.save()