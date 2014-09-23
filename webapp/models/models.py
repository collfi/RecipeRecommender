from sqlalchemy import Column, Integer, String
from database import Base


# SQL -----------
class User(Base):
  __tablename__ = 'users'
  login = Column(String(120), primary_key=True)
  fullname = Column(String(120), unique=False)
  email = Column(String(120), unique=True)
  password = Column(String(120), unique=False)

  def __init__(self, login=None, fullname=None, email=None, password=None):
    self.login = login
    self.fullname = fullname
    self.email = email
    self.password = password

  def __repr__(self):
    return '<User %r>' % (self.login)

class Recipe(Base):
  __tablename__ = 'recipes'
  id = Column(Integer, primary_key=True, autoincrement=True)
  userid = Column(String(120), unique=False)
  title = Column(String(120), unique=False)
  text = Column(String(1000), unique=False)
  tags = Column(String(1000), unique=False)

  def __init__(self, id = None, userid=None, title=None, text=None, tags=None):
    self.id = id
    self.userid = userid
    self.title = title
    self.text = text
    self.tags = tags

  def __repr__(self):
    return '<Recipe %r>' % (self.title)