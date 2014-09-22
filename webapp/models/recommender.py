from mongokit import Connection, Document
from datetime import datetime

def max_length(length):
  def validate(value):
    if len(value) <= length:
      return True
    raise Exception('%s must be at most %s chacters long' % length)
  return validate

class User(Document):
  __database__ = "recsys"
  __collection__ = "users"

  structure = {
    'login' : unicode,
    'rating' : [{'itemid' : int, 'value' : float, 'date_creation' : datetime}],
  }

  validators = {
    'login' : max_length(50)
  }

  use_dot_notation = True
  required_fields = ['login']

  def __repr__(self):
    return '<User %r>' % (self.login)