from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
  __tablename__ = 'users'
  login = Column(String(120), primary_key=True)
  fullname = Column(String(120), unique=True)
  email = Column(String(120), unique=True)
  password = Column(String(120), unique=True)

  def __init__(self, login=None, fullname=None, email=None, password=None):
    self.login = login
    self.fullname = fullname
    self.email = email
    self.password = password

  def __repr__(self):
    return '<User %r>' % (self.login)

