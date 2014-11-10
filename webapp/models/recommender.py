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
    #_id is login, every object in mongodb has _id attribute
    #'_id' : str,
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
    'date_creation' : datetime,
    'favorites' : [ unicode ],
    'ingredients' : [{'ingredient':unicode, 'number': unicode}],
    'tags' : [ unicode ]
  }
  default_values = {'date_creation':datetime.now()}

  use_dot_notation = True
  def print_favorites(self):
    print "favorites:", self.favorites

  def __repr__(self):
    return '<Recipe %r>' % (self._id)


class NonPersonal(Document):
  structure = {
      # ids of top5favorites recipes
      'tags' : [ unicode ],
      'topfavorites' : [ int ],
      'toprated' : [ int ],
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

  nonpcol = nonpcol.NonPersonal()
  nonpcol['_id'] = 1
  nonpcol['tags'].append(u"vegan")
  nonpcol['tags'].append(u"vegetarian")
  nonpcol['tags'].append(u"dairy-free")
  nonpcol['tags'].append(u"gluten-free")
  nonpcol['tags'].append(u"raw")
  nonpcol['tags'].append(u"low-carb")
  nonpcol['tags'].append(u"low-fat")
  nonpcol['tags'].append(u"low-calories")
  nonpcol['tags'].append(u"high-calories")
  nonpcol['tags'].append(u"drinks")
  nonpcol['tags'].append(u"lunch")
  nonpcol['tags'].append(u"dinner")
  nonpcol['tags'].append(u"breakfast")
  nonpcol['tags'].append(u"deserts")
  nonpcol['tags'].append(u"cookies")
  nonpcol['tags'].append(u"junkfood")
  nonpcol['tags'].append(u"french")
  nonpcol['tags'].append(u"italian")
  nonpcol['tags'].append(u"chinese")
  nonpcol['tags'].append(u"indian")
  nonpcol['tags'].append(u"thai")
  nonpcol['tags'].append(u"mexican")
  nonpcol['tags'].append(u"japanese")
  nonpcol['tags'].append(u"greek")
  nonpcol['tags'].append(u"czech")
  nonpcol['tags'].append(u"spicy")
  nonpcol['tags'].append(u"sweety")
  nonpcol['tags'].append(u"salty")
  nonpcol['tags'].append(u"bitter")
  nonpcol['tags'].append(u"oily")
  nonpcol['tags'].append(u"fatty")
  nonpcol['tags'].append(u"meat")
  nonpcol['tags'].append(u"fish")
  nonpcol['tags'].append(u"dairy")
  nonpcol['tags'].append(u"fruit")
  nonpcol['tags'].append(u"vegetables")
  nonpcol['tags'].append(u"seeds")
  nonpcol['tags'].append(u"sour")
  nonpcol.save()

  recipe = recipecol.Recipe()
  recipe['_id'] = 1
  recipe['ingredients'].append({'ingredient': u'eggs', 'number': u'5'})
  recipe['ingredients'].append({'ingredient': u'salt', 'number': u'3g'})
  recipe['ingredients'].append({'ingredient': u'sunflower oil', 'number': u'10 ml'})
  recipe['tags'].append(u'paleo')
  recipe['tags'].append(u'raw')
  recipe['tags'].append(u'vegetarian')
  recipe['tags'].append(u'gluten-free')
  recipe['tags'].append(u'low-carb')
  recipe['tags'].append(u'salty')
  recipe['tags'].append(u'breakfast')
  recipe.save()

  recipe2 = recipecol.Recipe()
  recipe2['_id'] = 2
  recipe2['ingredients'].append({'ingredient': u'honey', 'number': u'20g'})
  recipe2['ingredients'].append({'ingredient': u'rice', 'number': u'100g'})
  recipe2['ingredients'].append({'ingredient': u'salt', 'number': u'3g'})
  recipe2['ingredients'].append({'ingredient': u'sunflower oil', 'number': u'10 ml'})
  recipe2['tags'].append(u'vegan')
  recipe2['tags'].append(u'raw')
  recipe2['tags'].append(u'vegetarian')
  recipe2['tags'].append(u'gluten-free')
  recipe2['tags'].append(u'high-carb')
  recipe2['tags'].append(u'sweety')
  recipe2['tags'].append(u'breakfast')
  recipe2.save()

  recipe3 = recipecol.Recipe()
  recipe3['_id'] = 3
  recipe3['ingredients'].append({'ingredient': u'beef', 'number': u'200 g'})
  recipe3['ingredients'].append({'ingredient': u'rice', 'number': u'300 g'})
  recipe3['ingredients'].append({'ingredient': u'salt', 'number': u'3g'})
  recipe3['ingredients'].append({'ingredient': u'sunflower oil', 'number': u'10 ml'})
  recipe3['ingredients'].append({'ingredient': u'pepper', 'number': u'3 g'})
  recipe3['tags'].append(u'paleo')
  recipe3['tags'].append(u'raw')
  recipe3['tags'].append(u'meat')
  recipe3['tags'].append(u'high-protein')
  recipe3['tags'].append(u'low-carb')
  recipe3['tags'].append(u'salty')
  recipe3['tags'].append(u'lunch')
  recipe3.save()

  user = userscol.User()
  user['_id'] = 'admin'
  user.save()

  user2 = userscol.User()
  user2['_id'] = 'collfi'
  user2.save()

  user3 = userscol.User()
  user3['_id'] = 'cospel'
  user3.save()