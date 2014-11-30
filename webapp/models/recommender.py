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
    'fullname' : unicode,
    'email' : unicode,
    'password' : unicode, # in future we will encrypt the pass
    # value is rating, itemid is id of item
    'ratings' : [{'itemid' : int, 'value' : float, 'date_creation' : datetime}],
    # value is similarity
    'similar_users' : [{'userid' : unicode, 'value' : float}],
    # average rating
    'avgrating' : float,
    # these are ids of recipes which user has faved
    'favorites' : [ int],
    # ids of recommended (from collaborative filtering and content based) recipes sorted by expected rating
    'predicted': [{'itemid': int, 'value': float}],
  }
  use_dot_notation = True

  # returns none if user dont rate item with
  # itemid, else it returns value of his rating
  def getRating(self, itemid):
    for rate in self.ratings:
      if rate['itemid'] == itemid:
        return rate['value']
    return None

  def getHighlyRatedItems(self):
    vector = []
    for rate in self.ratings:
      if rate['value'] >= 4:
        vector.append(rate['itemid'])
    return vector

  def print_ratings(self):
    print "ratings:", self.ratings

  def print_favorites(self):
    print "favorites:", self.favorites

  def __repr__(self):
    return '<User %r>' % (self._id)

class Recipe(Document):
  structure = {
    # _id is id of recipe
    'userid' : unicode,
    'title' : unicode,
    'text' : unicode,
    #image = Column(Binary(9000), unique=False)
    'date_creation' : datetime,
    # ids of users which faved this recipe
    'favorites' : [ unicode ],
    'ingredients' : [{'ingredient':unicode, 'number': unicode}],
    'tags' : [ unicode ],
    'avgrating' : float,
    # interesting score by hacker news formula
    'interesting' : float,
    # value is similarity
    'similar_items' : [ {'itemid' : int, 'value' : float} ],
    # for how many people
    'serves' : int,
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
      # by interesting/hacker news formula
      'topinteresting' : [ int ]
  }
  use_dot_notation = True

  def get_tags(self):
    return sorted(self.tags)

  def print_top5favorites(self):
      print "top 5 favorites:", self.top5favorites

  def __repr__(self):
    return '<NonPersonal %r>' % (self._id)


def init_mongodbnew(mconnection):
  print("INITIALIZING MONGODB")
  userscol = mconnection['recsys'].users
  userscol.drop()
  recipecol = mconnection['recsys'].recipes
  recipecol.drop()
  nonpcol = mconnection['recsys'].nonpersonal
  nonpcol.drop()

  # region tags
  nonpcol = nonpcol.NonPersonal()
  nonpcol['_id'] = 1
  nonpcol['tags'].append(u"pasta")
  nonpcol['tags'].append(u"roasted")
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
  nonpcol['tags'].append(u"salad")
  nonpcol['tags'].append(u"seeds")
  nonpcol['tags'].append(u"dish")
  nonpcol['tags'].append(u"soup")
  nonpcol['tags'].append(u"sour")
  nonpcol['tags'].append(u"low-cost")
  nonpcol.save()

  # region recipes
  recipe = recipecol.Recipe()
  recipe['_id'] = 1
  recipe['userid'] = u'admin'
  recipe['title'] = u'Mixed eggs'
  recipe['text'] = u"""I wish you'd have given me this written question ahead of time so I
    could plan for it... I'm sure something will pop into my head here in
    the midst of this press conference, with all the pressure of trying to
    come up with answer, but it hadn't yet... I don't want to sound like
    I have made no mistakes. I'm confident I have. I just haven't - you
    just put me under the spot here, and maybe I'm not as quick on my feet
    as I should be in coming up with one."""
  recipe['ingredients'].append({'ingredient': u'eggs', 'number': u'5'})
  recipe['ingredients'].append({'ingredient': u'salt', 'number': u'3g'})
  recipe['ingredients'].append({'ingredient': u'sunflower oil', 'number': u'10 ml'})
  recipe['tags'].append(u'paleo')
  recipe['tags'].append(u'raw')
  recipe['tags'].append(u'vegetarian')
  recipe['tags'].append(u'ketogenic')
  recipe['tags'].append(u'gluten-free')
  recipe['tags'].append(u'low-carb')
  recipe['tags'].append(u'salty')
  recipe['tags'].append(u'breakfast')
  recipe['serves'] = 2
  recipe.save()

  recipe2 = recipecol.Recipe()
  recipe2['_id'] = 2
  recipe2['userid'] = u'admin'
  recipe2['title'] = u'Honey rice'
  recipe2['text'] = u"""I wish you'd have given me this written question ahead of time so I
    could plan for it... I'm sure something will pop into my head here in
    the midst of this press conference, with all the pressure of trying to
    come up with answer, but it hadn't yet... I don't want to sound like
    I have made no mistakes. I'm confident I have. I just haven't - you
    just put me under the spot here, and maybe I'm not as quick on my feet
    as I should be in coming up with one."""
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
  recipe2['serves'] = 2
  recipe2.save()

  recipe3 = recipecol.Recipe()
  recipe3['_id'] = 3
  recipe3['userid'] = u'collfi'
  recipe3['title'] = u'Roasted beef with rice'
  recipe3['text'] = u"""I wish you'd have given me this written question ahead of time so I
    could plan for it... I'm sure something will pop into my head here in
    the midst of this press conference, with all the pressure of trying to
    come up with answer, but it hadn't yet... I don't want to sound like
    I have made no mistakes. I'm confident I have. I just haven't - you
    just put me under the spot here, and maybe I'm not as quick on my feet
    as I should be in coming up with one."""
  recipe3['ingredients'].append({'ingredient': u'beef', 'number': u'200 g'})
  recipe3['ingredients'].append({'ingredient': u'rice', 'number': u'200 g'})
  recipe3['ingredients'].append({'ingredient': u'salt', 'number': u'3g'})
  recipe3['ingredients'].append({'ingredient': u'sunflower oil', 'number': u'10 ml'})
  recipe3['ingredients'].append({'ingredient': u'pepper', 'number': u'3 g'})
  recipe3['tags'].append(u'paleo')
  recipe3['tags'].append(u'raw')
  recipe3['tags'].append(u'meat')
  recipe3['tags'].append(u'high-protein')
  recipe3['tags'].append(u'salty')
  recipe3['tags'].append(u'lunch')
  recipe3['tags'].append(u'roasted')
  recipe3['serves'] = 2
  recipe3.save()

  recipe4 = recipecol.Recipe()
  recipe4['_id'] = 4
  recipe4['userid'] = u'cospel'
  recipe4['title'] = u'Roasted Pear Sauce'
  recipe4['text'] = u"""Preheat the oven to 350 degrees F.In a large bowl, toss the pears with melted butter.
  Pour the pears into a baking dish and roast, uncovered, for 20 to 25 minutes or until pears are tender,
  stirring once or twice. Set the cooked pears aside to cool. Add the pears back to the large bowl;
  add the honey and lemon juice. Using an immersion blender or stand up blender, blend the pear mixture until almost smooth."""
  recipe4['ingredients'].append({'ingredient': u'pears', 'number': u'3 large'})
  recipe4['ingredients'].append({'ingredient': u'butter', 'number': u'2 teaspoons'})
  recipe4['ingredients'].append({'ingredient': u'honey', 'number': u'1 tablespoon'})
  recipe4['ingredients'].append({'ingredient': u'lemon juice', 'number': u'1 tablespoon'})
  recipe4['ingredients'].append({'ingredient': u'walnuts', 'number': u'1/3 cup'})
  recipe4['tags'].append(u'sweety')
  recipe4['tags'].append(u'gluten-free')
  recipe4['tags'].append(u'vegetarian')
  recipe4['tags'].append(u'raw')
  recipe4['tags'].append(u'roasted')
  recipe4['tags'].append(u'vegan')
  recipe4['tags'].append(u'fruit')
  recipe4['serves'] = 4
  recipe4.save()

  recipe5 = recipecol.Recipe()
  recipe5['_id'] = 5
  recipe5['userid'] = u'cospel'
  recipe5['title'] = u'Balsamic Chicken with Mushrooms'
  recipe5['text'] = u""" Place the chicken breast in a plastic bag and pound thin with a mallet.
  Heat olive oil over medium-high heat in a skillet. Dredge the chicken in flour and coat it on both sides.
  Add the chicken to the pan and saute 5 minutes per side. Remove the chicken from the pan and set aside.
  Melt the margarine in the pan. Add the mushrooms and pepper and cook for 5 minutes. Add the balsamic vinegar
  to the pan and bring it to a boil to reduce the liquid. Add the chicken broth to the pan and simmer 2 more minutes.
  Add the chicken breast back to the pan and simmer for 5 minutes.""";
  recipe5['ingredients'].append({'ingredient': u'chicken breasts', 'number': u'1 kg'})
  recipe5['ingredients'].append({'ingredient': u'olive oil', 'number': u'1 tablespoon'})
  recipe5['ingredients'].append({'ingredient': u'flour', 'number': u'1/4 cup'})
  recipe5['ingredients'].append({'ingredient': u'mushrooms', 'number': u'300 g'})
  recipe5['ingredients'].append({'ingredient': u'black pepper', 'number': u'1/4 teaspoon'})
  recipe5['ingredients'].append({'ingredient': u'balsamic vinegar', 'number': u'1/3 cup'})
  recipe5['ingredients'].append({'ingredient': u'chicken broth sodium', 'number': u'1/2 cup'})
  recipe5['tags'].append(u'diabetic')
  recipe5['tags'].append(u'lunch')
  recipe5['tags'].append(u'meat')
  recipe5['tags'].append(u'vegetables')
  recipe5['serves'] = 4
  recipe5.save()

  recipe6 = recipecol.Recipe()
  recipe6['_id'] = 6
  recipe6['userid'] = u'cospel'
  recipe6['title'] = u'Eggs with avocado and salsa'
  recipe6['text'] = u""" Heat non-stick skillet over medium-high heat.
  Beat eggs in a small bowl, and pour into skillet. Cook for 1 minute and turn heat to medium-low.
  Finish cooking (about 2-4 minutes longer). Top with almonds, avocado and salsa.""";
  recipe6['ingredients'].append({'ingredient': u'eggs', 'number': u'4'})
  recipe6['ingredients'].append({'ingredient': u'avocado', 'number': u'1/2'})
  recipe6['ingredients'].append({'ingredient': u'almonds', 'number': u'1/2 cup'})
  recipe6['ingredients'].append({'ingredient': u'salsa', 'number': u'4 tablespoon'})
  recipe6['tags'].append(u'paleo')
  recipe6['tags'].append(u'raw')
  recipe6['tags'].append(u'gluten-free')
  recipe6['tags'].append(u'vegetarian')
  recipe6['tags'].append(u'ketogenic')
  recipe6['tags'].append(u'salty')
  recipe6['tags'].append(u'low-carb')
  recipe6['tags'].append(u'breakfast')
  recipe6['serves'] = 1
  recipe6.save()

  recipe7 = recipecol.Recipe()
  recipe7['_id'] = 7
  recipe7['userid'] = u'cospel'
  recipe7['title'] = u'Coconut chicken'
  recipe7['text'] = u""" Mix almond flour, shredded coconut and sea salt together in a bowl.
  Beat egg in separate bowl. Dip chicken breast in egg and roll in dry mixture.
  Heat a frying pan over medium heat and add coconut oil when hot. Pan fry chicken until fully
  cooked. If the crust starts to brown and your chicken isn't fully cooked yet
   (this will depend on the size of the chicken breast), take it out of the pan and place it
   in the oven on a baking sheet at 350F for 5-10 minutes covered with foil.""";
  recipe7['ingredients'].append({'ingredient': u'chicken breasts', 'number': u'500 g'})
  recipe7['ingredients'].append({'ingredient': u'almond flour', 'number': u'1/4 cup'})
  recipe7['ingredients'].append({'ingredient': u'shredded coconut', 'number': u'1/4 cup'})
  recipe7['ingredients'].append({'ingredient': u'salt', 'number': u'1/4 tablespoon'})
  recipe7['ingredients'].append({'ingredient': u'eggs', 'number': u'1'})
  recipe7['ingredients'].append({'ingredient': u'coconut oil', 'number': u'2 tablespoon'})
  recipe7['tags'].append(u'breakfast')
  recipe7['tags'].append(u'paleo')
  recipe7['tags'].append(u'raw')
  recipe7['tags'].append(u'ketogenic')
  recipe7['tags'].append(u'low-carb')
  recipe7['tags'].append(u'lunch')
  recipe7['tags'].append(u"meat")
  recipe7['serves'] = 3
  recipe7.save()

  recipe8 = recipecol.Recipe()
  recipe8['_id'] = 8
  recipe8['userid'] = u'cospel'
  recipe8['title'] = u'Honey rice dish'
  recipe8['text'] = u""" Combine rice, raisins, milk, honey, and butter in a
  saucepan. Bring the mixture to a boil, reduce the heat, and let it simmer for
  15 minutes; stirring occasionally. Stir in lemon rind and juice. Serve the rice
  in bowls and garnish (optional) with cinnamon and slivered almonds.""";
  recipe8['ingredients'].append({'ingredient': u'rice', 'number': u'300 g'})
  recipe8['ingredients'].append({'ingredient': u'raisins', 'number': u'1/2 cup'})
  recipe8['ingredients'].append({'ingredient': u'milk', 'number': u'1/2 cup'})
  recipe8['ingredients'].append({'ingredient': u'honey', 'number': u'1/2 cup'})
  recipe8['ingredients'].append({'ingredient': u'butter', 'number': u'2 tablespoon'})
  recipe8['ingredients'].append({'ingredient': u'lemon rind', 'number': u'1 teaspoon'})
  recipe8['ingredients'].append({'ingredient': u'lemon juice', 'number': u'1 tablespoon'})
  recipe8['ingredients'].append({'ingredient': u'cinnamon', 'number': u'1/8 teaspoon'})
  recipe8['tags'].append(u'vegetarian')
  recipe8['tags'].append(u'vegan')
  recipe8['tags'].append(u'high-carb')
  recipe8['tags'].append(u'soup')
  recipe8['tags'].append(u'lunch')
  recipe8['tags'].append(u'sweety')
  recipe8['tags'].append(u'dairy')
  recipe8['serves'] = 3
  recipe8.save()

  recipe9 = recipecol.Recipe()
  recipe9['_id'] = 9
  recipe9['userid'] = u'qacer'
  recipe9['title'] = u'Balsamic green bean salad'
  recipe9['text'] = u""" Bring a pot of salted water to a boil. Add the green beans and blanch
  for 2-3 minutes. The beans should be just barely cooked through and still crisp. Prepare a large
  bowl of ice water while the beans are cooking. Remove beans from hot water and place into ice bath
  to stop the cooking. Drain. Place the green beans and red onion in a large bowl. Toss in the olive
  oil to coat. Sprinkle in the balsamic and season with salt and freshly ground black pepper. Top with
  chopped walnuts to serve.""";
  recipe9['ingredients'].append({'ingredient': u'green beans', 'number': u'1 kg'})
  recipe9['ingredients'].append({'ingredient': u'red onion', 'number': u'1/2 chopped'})
  recipe9['ingredients'].append({'ingredient': u'olive oil', 'number': u'3 tablespoon'})
  recipe9['ingredients'].append({'ingredient': u'balsamic vinegar', 'number': u'1/2 cup'})
  recipe9['ingredients'].append({'ingredient': u'chopped walnuts', 'number': u'2 tablespoon'})
  recipe9['ingredients'].append({'ingredient': u'salt', 'number': u'1 teaspoon'})
  recipe9['ingredients'].append({'ingredient': u'black pepper', 'number': u'1 tablespoon'})
  recipe9['tags'].append(u'vegetarian')
  recipe9['tags'].append(u'vegan')
  recipe9['tags'].append(u'low-carb')
  recipe9['tags'].append(u'vegetables')
  recipe9['tags'].append(u'lunch')
  recipe9['tags'].append(u'salad')
  recipe9['serves'] = 5
  recipe9.save()

  recipe10 = recipecol.Recipe()
  recipe10['_id'] = 10
  recipe10['userid'] = u'qacer'
  recipe10['title'] = u'Cauliflower salad'
  recipe10['text'] = u""" Grate the entire head of cauliflower (stem and leaves omitted),
  so that it resembles quinoa or rice. I used a grater and accomplished the task
   by hand, although a food processor would be a much faster and easier alternative. Place into a large mixing bowl.
  Dice tomatoes and finely chop cilantro. Mix together the tomatoes, cilantro, and grated cauliflower.
  Add in the lemon juice, lime juice, sea salt, black pepper, and garlic powder. Mix well.""";
  recipe10['ingredients'].append({'ingredient': u'cauliflower', 'number': u'1 head'})
  recipe10['ingredients'].append({'ingredient': u'tomatoe', 'number': u'4'})
  recipe10['ingredients'].append({'ingredient': u'cilantro', 'number': u'1 cup'})
  recipe10['ingredients'].append({'ingredient': u'lemon juice', 'number': u'1/4 cup'})
  recipe10['ingredients'].append({'ingredient': u'lime juice', 'number': u'1/4 cup'})
  recipe10['ingredients'].append({'ingredient': u'garlic', 'number': u'1'})
  recipe10['ingredients'].append({'ingredient': u'salt', 'number': u'5 gr'})
  recipe10['ingredients'].append({'ingredient': u'black pepper', 'number': u'1 gr'})
  recipe10['tags'].append(u'vegetarian')
  recipe10['tags'].append(u'vegan')
  recipe10['tags'].append(u'raw')
  recipe10['tags'].append(u'low-carb')
  recipe10['tags'].append(u'vegetables')
  recipe10['tags'].append(u'lunch')
  recipe10['tags'].append(u'salad')
  recipe10['serves'] = 2
  recipe10.save()

  recipe11 = recipecol.Recipe()
  recipe11['_id'] = 11
  recipe11['userid'] = u'qacer'
  recipe11['title'] = u'Paleo porridge'
  recipe11['text'] = u"""Put it in a bowl, dust some ground cinnamon on top and serve with
   coconut milk and some lingonberry jam, applesauce, grated apple/pear,
    or berries.""";
  recipe11['ingredients'].append({'ingredient': u'eggs', 'number': u'2'})
  recipe11['ingredients'].append({'ingredient': u'coconut flour', 'number': u'1 tablespoon'})
  recipe11['ingredients'].append({'ingredient': u'coconut milk', 'number': u'1 dl'})
  recipe11['ingredients'].append({'ingredient': u'salt', 'number': u'1 teaspoon'})
  recipe11['ingredients'].append({'ingredient': u'fruit', 'number': u'of your choice'})
  recipe11['tags'].append(u'vegetarian')
  recipe11['tags'].append(u'vegan')
  recipe11['tags'].append(u'raw')
  recipe11['tags'].append(u'paleo')
  recipe11['tags'].append(u'breakfast')
  recipe11['tags'].append(u'fruit')
  recipe11['serves'] = 1
  recipe11.save()

  recipe12 = recipecol.Recipe()
  recipe12['_id'] = 12
  recipe12['userid'] = u'collfi'
  recipe12['title'] = u'Classic tomato spaghetti'
  recipe12['text'] = u"""Put a saucepan on a medium heat and add 1 tablespoon of olive
  oil and the onion, then cook for around 7 minutes, or until soft and lightly golden.
  Stir in the garlic and basil stalks for a few minutes, then add the fresh or tinned
  tomatoes and the vinegar. Add the spaghetti and cook according to packet instructions
  to it. Use the timings on the packet instructions as a guide, but try some just before the time
  is up to make sure it's perfectly cooked..""";
  recipe12['ingredients'].append({'ingredient': u'fresh basil', 'number': u''})
  recipe12['ingredients'].append({'ingredient': u'onion', 'number': u'1'})
  recipe12['ingredients'].append({'ingredient': u'garlic', 'number': u'2 cloves'})
  recipe12['ingredients'].append({'ingredient': u'tomatoes', 'number': u'1 kg'})
  recipe12['ingredients'].append({'ingredient': u'olive oil', 'number': u''})
  recipe12['ingredients'].append({'ingredient': u'balsamic vinegar', 'number': u'1 tablespoon'})
  recipe12['ingredients'].append({'ingredient': u'salt', 'number': u'5 g'})
  recipe12['ingredients'].append({'ingredient': u'black pepper', 'number': u'3 g'})
  recipe12['ingredients'].append({'ingredient': u'spaghetti', 'number': u'500 g'})
  recipe12['ingredients'].append({'ingredient': u'parmesan cheese', 'number': u'15 g'})
  recipe12['tags'].append(u'vegetarian')
  recipe12['tags'].append(u'lunch')
  recipe12['tags'].append(u'italian')
  recipe12['tags'].append(u'pasta')
  recipe12['serves'] = 1
  recipe12.save()



  # region users
  user = userscol.User()
  user['_id'] = 'admin'
  user['fullname'] = u'admin'
  user['email'] = u'cospelthetraceur@gmail.com'
  user['password'] = u'admin'
  user.save()

  user2 = userscol.User()
  user2['_id'] = 'collfi'
  user2['fullname'] = u'Boris Valentovic'
  user2['email'] = u'collfijepan@gmail.com'
  user2['password'] = u'collfi'
  user2.save()

  user3 = userscol.User()
  user3['_id'] = 'cospel'
  user3['fullname'] = u'Michal Lukac'
  user3['email'] = u'cospelthetraceur@gmail.com'
  user3['password'] = u'cospel'
  user3.save()

  user4 = userscol.User()
  user4['_id'] = 'qacer'
  user4['fullname'] = u'Jakub Kusnier'
  user4['email'] = u'qacer8@gmail.com'
  user4['password'] = u'qacer'
  user4.save()



if __name__ == '__main__':
  pass