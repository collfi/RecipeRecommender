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
    'rating' : [{'itemid' : int, 'value' : float, 'date_creation' : datetime}],
  }
  use_dot_notation = True
  #required_fields = ['_id']
  #default_values = {...}
  def __repr__(self):
    return '<User %r>' % (self._id)

def init_mongodb(mconnection):
  userscol = mconnection['recsys'].users
  userscol.drop()
  user = userscol.User()
  user['_id'] = 'admin'
  user.save()

