# coding=utf-8
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
    # value is similarity, type = 1tags, 2ingredients
    'similar_items' : [ {'itemid' : int, 'value' : float, 'type' : int} ],
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
  nonpcol['tags'].append(u"american")
  nonpcol['tags'].append(u"spicy")
  nonpcol['tags'].append(u"sweet")
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
  recipe2['tags'].append(u'sweet')
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
  recipe4['tags'].append(u'sweet')
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
  recipe8['tags'].append(u'sweet')
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

  recipe13 = recipecol.Recipe()
  recipe13['_id'] = 13
  recipe13['userid'] = u'collfi'
  recipe13['title'] = u'Gluten-Free Chili'
  recipe13['text'] = u"""Pour the olive oil into a slow cooker or Crock Pot. Add the garlic and onion and
  stir to coat. Add in the remaining ingredients. Break apart the tomatoes a bit. Cook on low or high according
  to the manufacturers instruction for your particular make and model. Go do something creative. Dance. Read.
  Draw with crayons. Before serving, taste for seasoning adjustments- add a bit of raw organic agave nectar
  to tone down the heat. Add lime juice to brighten the flavors.Omnivores add your favorite cooked organic
  sausage, browned grass fed organic ground beef, or cooked free-range organic turkey or  chicken pieces,
  if you like. Serve with wedges of Sweet Potato Cornbread or New Irish Soda Bread with Millet.""";
  recipe13['ingredients'].append({'ingredient': u'olive oil', 'number': u'1 tablespoon'})
  recipe13['ingredients'].append({'ingredient': u'garlic', 'number': u'4 cloves'})
  recipe13['ingredients'].append({'ingredient': u'red onion', 'number': u'1'})
  recipe13['ingredients'].append({'ingredient': u'jalapeños', 'number': u'2'})
  recipe13['ingredients'].append({'ingredient': u'yellow pepper', 'number': u'1'})
  recipe13['ingredients'].append({'ingredient': u'green pepper', 'number': u'1'})
  recipe13['ingredients'].append({'ingredient': u'carrot', 'number': u'2'})
  recipe13['ingredients'].append({'ingredient': u'sweet potato', 'number': u'1'})
  recipe13['ingredients'].append({'ingredient': u'gluten-free broth', 'number': u'2 cup'})
  recipe13['ingredients'].append({'ingredient': u'roasted tomatoes', 'number': u'1 can'})
  recipe13['ingredients'].append({'ingredient': u'white beans', 'number': u'1 can'})
  recipe13['ingredients'].append({'ingredient': u'cumin', 'number': u'1 teaspoon'})
  recipe13['ingredients'].append({'ingredient': u'curry', 'number': u'1 teaspoon'})
  recipe13['tags'].append(u'vegetarian')
  recipe13['tags'].append(u'lunch')
  recipe13['tags'].append(u'vegan')
  recipe13['tags'].append(u"gluten-free")
  recipe13['tags'].append(u"mexican")
  recipe13['tags'].append(u"spicy")
  recipe13['serves'] = 4
  recipe13.save()

  recipe14 = recipecol.Recipe()
  recipe14['_id'] = 14
  recipe14['userid'] = u'collfi'
  recipe14['title'] = u'Sea bass, fennel & grapefruit ceviche'
  recipe14['text'] = u"""Slice the fish into 1cm strips, put them in a bowl and pop them in the fridge. In
  a separate bowl or jam jar, mix the lemon juice, salt, chilli and garlic, then pop this in the fridge. Cut
  the top and bottom off the grapefruit, carefully peel away the skin, then separate them into segments and put
  these in a bowl, squeezing the juice from a few segments into the bowl. When your guests are ready to eat, get
  the fish out of the fridge and combine it with the fennel, grapefruit and most of the mint leaves. Give
  the marinade in the bowl or jam jar a mix, then pour the juices over the fish mixture, delicately toss together
  and leave for 2 minutes. Serve simply, on a big platter, with the remaining mint leaves and fennel tops
  sprinkled over, adding a little drizzle of olive oil and a few grinds of black pepper.""";
  recipe14['ingredients'].append({'ingredient': u'sea bass', 'number': u'500 g'})
  recipe14['ingredients'].append({'ingredient': u'lemon', 'number': u'2'})
  recipe14['ingredients'].append({'ingredient': u'sea salt', 'number': u'2 teaspoon'})
  recipe14['ingredients'].append({'ingredient': u'red chilli', 'number': u'2'})
  recipe14['ingredients'].append({'ingredient': u'garlic', 'number': u'1 clove'})
  recipe14['ingredients'].append({'ingredient': u'grapefruit', 'number': u'1'})
  recipe14['ingredients'].append({'ingredient': u'fennel', 'number': u'2'})
  recipe14['ingredients'].append({'ingredient': u'mint', 'number': u'small bunch'})
  recipe14['ingredients'].append({'ingredient': u'olive oil', 'number': u'1 teaspoon'})
  recipe14['tags'].append(u"fish")
  recipe14['tags'].append(u"spicy")
  recipe14['tags'].append(u"dinner")
  recipe14['tags'].append(u"sour")
  recipe14['serves'] = 4
  recipe14.save()

  recipe15 = recipecol.Recipe()
  recipe15['_id'] = 15
  recipe15['userid'] = u'cospel'
  recipe15['title'] = u'Coconut cheesecake'
  recipe15['ingredients'].append({'ingredient': u'sea bass', 'number': u'500 g'})
  recipe15['text'] = u"""Place the cashew nuts in a bowl, cover with cold water, then set aside to soak for at
  least 4 hours, or preferably overnight. Grease a 20cm springform cake tin with margarine, sprinkle in
  the desiccated coconut, then give the tin a good shake so that it's evenly distributed. Place the dates
  in a bowl, cover with warm water, then leave to soak for around 10 minutes, or until softened. Drain and add
  to a food processor, then blitz to a rough paste. Add the almonds and hazelnuts, then blitz to a chunky crumb
  consistency. Spoon the mixture into the prepared cake tin, patting and smoothing it out evenly with wet
  hands. Give the food processor bowl a quick rinse, then drain and add the cashew nuts along with lemon juice,
  honey and coconut oil. Halve the vanilla pods lengthways, scrape out the seeds, then add to the processor,
  discarding the pods. Blitz until smooth and combined, then have a taste and add more honey if you think it
  needs it. Carefully pour the cashew mixture on top of the crumb base, smoothing it out evenly. Place the tin
  onto a tray, then gently tap it on a work surface to get rid of any bubbles. Pop in the freezer for around 2
  hours, or until set. Meanwhile, make the strawberry drizzle. Hull and roughly chop the strawberries, then
  place into a bowl with the sugar and lemon juice. Leave for around 5 minutes to soak, then place in a
  liquidiser and blitz until smooth. When you're ready to serve, remove the cheesecake from the freezer, then
  allow to thaw slightly for around 10 minutes. Serve the strawberry drizzle alongside the cheesecake, then
  tuck in!""";
  recipe15['ingredients'].append({'ingredient': u'cashew nuts', 'number': u'300 g'})
  recipe15['ingredients'].append({'ingredient': u'dairy-free margarine', 'number': u'100 g'})
  recipe15['ingredients'].append({'ingredient': u'dates', 'number': u'200 g'})
  recipe15['ingredients'].append({'ingredient': u'almonds', 'number': u'150 g'})
  recipe15['ingredients'].append({'ingredient': u'hazelnuts', 'number': u'100 g'})
  recipe15['ingredients'].append({'ingredient': u'lemon', 'number': u'4'})
  recipe15['ingredients'].append({'ingredient': u'honey', 'number': u'250 g'})
  recipe15['ingredients'].append({'ingredient': u'coconut oil', 'number': u'165 ml'})
  recipe15['ingredients'].append({'ingredient': u'vanilla pod', 'number': u'2'})
  recipe15['ingredients'].append({'ingredient': u'strawberry', 'number': u'400 g'})
  recipe15['ingredients'].append({'ingredient': u'sugar', 'number': u'2 tablespoon'})
  recipe15['tags'].append(u"sweet")
  recipe15['tags'].append(u"fruit")
  recipe15['tags'].append(u"dairy-free")
  recipe15['tags'].append(u"vegan")
  recipe15['tags'].append(u"vegetarian")
  recipe15['tags'].append(u"deserts")
  recipe15['serves'] = 12
  recipe15.save()

  recipe16 = recipecol.Recipe()
  recipe16['_id'] = 16
  recipe16['userid'] = u'collfi'
  recipe16['title'] = u'Mac \'n\' cheese'
  recipe16['text'] = u"""Preheat the oven to 180C/350F/gas 4. Cook the macaroni according to the packet
  instructions in a large pan of salted boiling water. Meanwhile, peel and halve the onion, then place in
  a small pan over a medium heat with the milk. Slowly bring to the boil, then remove from the heat. Pick out
  and discard the onion, then set aside. Melt the margarine in another pan over a medium heat, then add
  the flour, stirring continuously until it forms a paste this is the roux. Gradually add the warm milk
  a little at a time, whisking continuously until smooth. Bring to the boil, then simmer for around 10 minutes,
  or until thickened. Stir in the mustard and nutritional yeast flakes, grate and stir in the vegan cheese
  (if using), then season to taste with salt and pepper. Drain and add the macaroni to the sauce, then toss to
  coat. Transfer the mixture to an ovenproof baking dish (roughly 20cm x 30cm), then set aside. Peel and finely
  slice the garlic, then pick the thyme leaves, discarding the stalks. Add to a medium pan over a medium heat
  with a splash of oil. Cook for 2 to 3 minutes, or until golden, then transfer to a food processor with the
  breadcrumbs and a splash of oil. Blitz until combined and roughly chopped, then sprinkle over the pasta.
  Place the dish in the hot oven for 20 to 25 minutes, or until golden and bubbling. Leave to stand for around
  5 minutes, then serve with seasonal greens.""";
  recipe16['ingredients'].append({'ingredient': u'macaroni', 'number': u'350 g'})
  recipe16['ingredients'].append({'ingredient': u'sea salt', 'number': u'2 teaspoon'})
  recipe16['ingredients'].append({'ingredient': u'black pepper', 'number': u'1/2 teaspoon'})
  recipe16['ingredients'].append({'ingredient': u'onion', 'number': u'1'})
  recipe16['ingredients'].append({'ingredient': u'soya milk', 'number': u'1 litre'})
  recipe16['ingredients'].append({'ingredient': u'dairy-free margarine', 'number': u'100 g'})
  recipe16['ingredients'].append({'ingredient': u'plain flour', 'number': u'85 g'})
  recipe16['ingredients'].append({'ingredient': u'mustard', 'number': u'1 teaspoon'})
  recipe16['ingredients'].append({'ingredient': u'yeast', 'number': u'2 tablespoon'})
  recipe16['ingredients'].append({'ingredient': u'garlic', 'number': u'5 cloves'})
  recipe16['ingredients'].append({'ingredient': u'thyme', 'number': u'1/2 bunch'})
  recipe16['ingredients'].append({'ingredient': u'olive oil', 'number': u'1 teaspoon'})
  recipe16['ingredients'].append({'ingredient': u'breadcrumbs', 'number': u'40 g'})
  recipe16['tags'].append(u"vegan")
  recipe16['tags'].append(u'vegetarian')
  recipe16['tags'].append(u"pasta")
  recipe16['tags'].append(u"dairy-free")
  recipe16['tags'].append(u"lunch")
  recipe16['tags'].append(u"american")
  recipe16['serves'] = 6
  recipe16.save()

  recipe17 = recipecol.Recipe()
  recipe17['_id'] = 17
  recipe17['userid'] = u'admin'
  recipe17['title'] = u'Chicken in milk'
  recipe17['text'] = u"""Preheat the oven to 190C/375F/gas 5, and find a snug-fitting pot for the chicken.
  Season it generously all over, and fry it in a little olive oil, turning the chicken to get an even colour
  all over, until golden. Remove from the heat, put the chicken on a plate, and throw away the oil left in the
  pot. This will leave you with tasty sticky goodness at the bottom of the pan which will give you a lovely
  caramel flavour later on. Put your chicken back in the pot with the rest of the ingredients, and cook in the
  preheated oven for 1 hours. Baste with the cooking juice when you remember. The lemon zest will sort of split
  the milk, making a sauce which is absolutely fantastic. To serve, pull the meat off the bones and divide it
  onto your plates. Spoon over plenty of juice and the little curds. Serve with wilted spinach or greens and
  some mashed potato.""";
  recipe17['ingredients'].append({'ingredient': u'chicken', 'number': u'1500 g'})
  recipe17['ingredients'].append({'ingredient': u'sea salt', 'number': u'2 teaspoon'})
  recipe17['ingredients'].append({'ingredient': u'black pepper', 'number': u'1/2 teaspoon'})
  recipe17['ingredients'].append({'ingredient': u'olive oil', 'number': u'1 teaspoon'})
  recipe17['ingredients'].append({'ingredient': u'cinnamon', 'number': u'1/2 stick'})
  recipe17['ingredients'].append({'ingredient': u'sage', 'number': u'1 handful'})
  recipe17['ingredients'].append({'ingredient': u'lemon', 'number': u'2'})
  recipe17['ingredients'].append({'ingredient': u'garlic', 'number': u'10 cloves'})
  recipe17['ingredients'].append({'ingredient': u'milk', 'number': u'565 ml'})
  recipe17['tags'].append(u"meat")
  recipe17['tags'].append(u"dairy")
  recipe17['tags'].append(u"lunch")
  recipe17['tags'].append(u"roasted")
  recipe17['tags'].append(u"low-carb")
  recipe17['serves'] = 5
  recipe17.save()

  recipe18 = recipecol.Recipe()
  recipe18['_id'] = 18
  recipe18['userid'] = u'cospel'
  recipe18['title'] = u'A killer mac \'n\' cheese'
  recipe18['text'] = u"""Get a large pan of salted water on the boil. Melt the butter in a large ovenproof saucepan
  over a low heat, then add the flour and turn the heat up to medium, stirring all the time, until you get
  a paste this is your roux. Add all the sliced garlic don't worry about the amount because each slice will
  caramelise like toffee in the roux. Keep cooking and stirring until golden and the garlic is nice and sticky.
  Add the bay leaves and slowly whisk in the milk a little at a time to ensure you get a nice smooth sauce.
  Bring the mixture to the boil, then leave it on a low heat to simmer and tick away, stirring occasionally.
  Preheat your oven to 220C/425F/gas 7. Add the pasta to the pan of boiling salted water and cook according to
  the packet instructions. Meanwhile, roughly chop the tomatoes on a board and season them well with salt and
  pepper. Drain the pasta and add it immediately to the sauce. Give it a good stir and take the pan off the heat.
  Stir in your grated cheeses, chopped tomatoes and thyme leaves. A little Worcestershire sauce added now is
  nice, and so is a little grating or two of nutmeg. Now work on the flavour taste it and season it until it's
  hitting the right spot. You want it to be slightly too wet because it will thicken up again in the oven, so
  add a splash of water if needed. If you've made your sauce in an ovenproof casserole-type pan, leave
  everything in there; if not, transfer it to a deep earthenware dish. Bake it for 30 minutes in the oven, until
  golden, bubbling, crispy and delicious. While it's cooking, put your breadcrumbs and thyme into a pan with
  a few drizzles of olive oil over a medium heat. Stir and toss the crumbs around until crunchy and golden all
  over. Remove from the heat and tip into a nice bowl. Serve your macaroni cheese in the centre of the table,
  with your bowl of crispy breadcrumbs for sprinkling over, and a lovely green salad.""";
  recipe18['ingredients'].append({'ingredient': u'macaroni', 'number': u'600 g'})
  recipe18['ingredients'].append({'ingredient': u'sea salt', 'number': u'2 teaspoon'})
  recipe18['ingredients'].append({'ingredient': u'black pepper', 'number': u'1/2 teaspoon'})
  recipe18['ingredients'].append({'ingredient': u'olive oil', 'number': u'1 teaspoon'})
  recipe18['ingredients'].append({'ingredient': u'butter', 'number': u'45 g'})
  recipe18['ingredients'].append({'ingredient': u'plain flour', 'number': u'3 tablespoon'})
  recipe18['ingredients'].append({'ingredient': u'bay leaf', 'number': u'6'})
  recipe18['ingredients'].append({'ingredient': u'garlic', 'number': u'10 cloves'})
  recipe18['ingredients'].append({'ingredient': u'milk', 'number': u'1 litre'})
  recipe18['ingredients'].append({'ingredient': u'tomatoes', 'number': u'8'})
  recipe18['ingredients'].append({'ingredient': u'cheddar', 'number': u'150 g'})
  recipe18['ingredients'].append({'ingredient': u'parmesan', 'number': u'150 g'})
  recipe18['ingredients'].append({'ingredient': u'Worcestershire sauce', 'number': u'2 teaspoon'})
  recipe18['tags'].append(u'vegetarian')
  recipe18['tags'].append(u"pasta")
  recipe18['tags'].append(u"dairy")
  recipe18['tags'].append(u"lunch")
  recipe18['tags'].append(u"dinner")
  recipe18['tags'].append(u"american")
  recipe16['serves'] = 8
  recipe18.save()

  recipe19 = recipecol.Recipe()
  recipe19['_id'] = 19
  recipe19['userid'] = u'filip'
  recipe19['title'] = u'Salmon with spring pea and citrus salad'
  recipe19['text'] = u"""Preheat oven to 425F. Season both sides of fresh salmon filets with sea salt and black
  pepper. If you are using frozen filets, wait to season until a few minutes in to cooking so it will stick.
  Place filets on a broiler pan (or use a wire rack over a baking sheet) and place in the oven. Bake 15-18
  minutes for fresh salmon or 30-35 minutes for frozen, or until salmon flakes easily with a fork and reaches
  an internal temperature of 145F. Meanwhile, in a large mixing bowl, combine mixed greens (or pea shoots),
  sugar snap peas, radish slices, sunflower seeds, orange juice, lemon juice (or segments) and olive oil. Toss
  to coat and season slightly with sea salt and black pepper, if desired. Divide greens into two salad bowls.
  Top with warm or cooled salmon to serve.""";
  recipe19['ingredients'].append({'ingredient': u'salmon', 'number': u'350 g'})
  recipe19['ingredients'].append({'ingredient': u'sea salt', 'number': u'1/2 tablespoon'})
  recipe19['ingredients'].append({'ingredient': u'black pepper', 'number': u'1/4 tablespoon'})
  recipe19['ingredients'].append({'ingredient': u'pea shoots', 'number': u'250 g'})
  recipe19['ingredients'].append({'ingredient': u'pea', 'number': u'1 cup'})
  recipe19['ingredients'].append({'ingredient': u'radish', 'number': u'1'})
  recipe19['ingredients'].append({'ingredient': u'sunflower seeds', 'number': u'1/3 cup'})
  recipe19['ingredients'].append({'ingredient': u'orange', 'number': u'1/2'})
  recipe19['ingredients'].append({'ingredient': u'lemon', 'number': u'1/2'})
  recipe19['ingredients'].append({'ingredient': u'olive oil', 'number': u'2 tablespoon'})
  recipe19['tags'].append(u'fish')
  recipe19['tags'].append(u"paleo")
  recipe19['tags'].append(u"salad")
  recipe19['tags'].append(u"seeds")
  recipe19['serves'] = 2
  recipe19.save()

  recipe20 = recipecol.Recipe()
  recipe20['_id'] = 20
  recipe20['userid'] = u'filip'
  recipe20['title'] = u'Danish meat loaf'
  recipe20['text'] = u"""Preheat oven to 400 F. Add coconut oil or fat of choice to a large saut pan over medium
  heat. When pan is hot, add onion and mushrooms and saut until softened and slightly browned (about 10 minutes).
   While the onions and mushrooms cook, mix ground meat, egg, almond flour, coconut milk, sea salt (optional),
   and black pepper in a bowl. Combine mushrooms and onions with meat loaf mixture. Shape into a loaf in
   an ungreased baking pan, and add the bacon strips across the top of loaf. Bake for 50-65 minutes, or until
   fully cooked. There might be "soup" surrounding the loaf which you can just throw away or freeze for later
   use as stock in a real soup.""";
  recipe20['ingredients'].append({'ingredient': u'pork', 'number': u'250 g'})
  recipe20['ingredients'].append({'ingredient': u'turkey', 'number': u'250 g'})
  recipe20['ingredients'].append({'ingredient': u'egg', 'number': u'1'})
  recipe20['ingredients'].append({'ingredient': u'almond flour', 'number': u'4 tablespoon'})
  recipe20['ingredients'].append({'ingredient': u'sea salt', 'number': u'1 tablespoon'})
  recipe20['ingredients'].append({'ingredient': u'black pepper', 'number': u'1/2 tablespoon'})
  recipe20['ingredients'].append({'ingredient': u'coconut milk', 'number': u'1/4 cup'})
  recipe20['ingredients'].append({'ingredient': u'onion', 'number': u'1'})
  recipe20['ingredients'].append({'ingredient': u'button mushrooms', 'number': u'6'})
  recipe20['ingredients'].append({'ingredient': u'bacon', 'number': u'3 slices'})
  recipe20['tags'].append(u'meat')
  recipe20['tags'].append(u"paleo")
  recipe20['tags'].append(u"fatty")
  recipe20['tags'].append(u"gluten-free")
  recipe20['serves'] = 4
  recipe20.save()

  recipe21 = recipecol.Recipe()
  recipe21['_id'] = 21
  recipe21['userid'] = u'radek'
  recipe21['title'] = u'Dark Chocolate Mousse'
  recipe21['text'] = u"""Place a medium sauce pan over medium-low heat. Break the chocolate into large chunks
  and place in the pan with the water and a pinch of salt. Stir with a whisk to melt the chocolate into
  the water. It should look like old fashioned chocolate syrup: smooth, slightly shiny, and liquidy. Turn off
  the heat. Dump the ice cubes into a large bowl and add about 1 cup of cold water. Place a slightly smaller
  bowl inside the large bowl and scrape the hot chocolate sauce into the top bowl. Grab a wire whisk and whisk
  that stuff like your life depends on it. The ice bath underneath cools the cbocolate, and the whisking action
  incorporates air that create the fluffy, mousse-like texture. It took me about 3-4 minutes to get to
  the desired consistency. At first, it seemed like it would never happen. My arm may have gotten very tired.
  But I kept going and you will, too! If your mousse suddenly cools and thickens too quickly, you can re-melt
  it and start over. So forgiving! (See the original recipe for troubleshooting, but I had no problems.) Spoon
  the mousse into serving dishes and refrigerate if youre not going to eat it immediately. If youre making
  whipped cream, remove your bowl and beater from the freezer. Spoon half the thickened, chilled coconut milk
  into the mixing bowl and save the rest for a curry. Add the extract to the bowl, then beat the coconut milk
  for 5 or so minutes until it takes on the texture of whipped cream. Dollop on top of the mousse, then sprinkle
  the top of the dessert with a pinch of coarse sea salt. Serve and relish the compliments.""";
  recipe21['ingredients'].append({'ingredient': u'dark chocolate', 'number': u'100 g'})
  recipe21['ingredients'].append({'ingredient': u'water', 'number': u'75 ml'})
  recipe21['ingredients'].append({'ingredient': u'salt', 'number': u'1/4 teaspoon'})
  recipe21['ingredients'].append({'ingredient': u'ice', 'number': u'2 cubes'})
  recipe21['ingredients'].append({'ingredient': u'coconut milk', 'number': u'1 can'})
  recipe21['ingredients'].append({'ingredient': u'vanilla extract', 'number': u'1/4 teaspoon'})
  recipe21['ingredients'].append({'ingredient': u'almond extract', 'number': u'1/4 teaspoon'})
  recipe21['tags'].append(u'drinks')
  recipe21['tags'].append(u"desert")
  recipe21['tags'].append(u"vegan")
  recipe21['tags'].append(u"vegetarian")
  recipe21['tags'].append(u"low-carb")
  recipe21['serves'] = 4
  recipe21.save()

  recipe22 = recipecol.Recipe()
  recipe22['_id'] = 22
  recipe22['userid'] = u'radek'
  recipe22['title'] = u'Broccoli and Cheese Mini Egg Omelets'
  recipe22['text'] = u"""Preheat oven to 350°. Steam broccoli with a little water for about 6-7 minutes.
  When broccoli is cooked, crumble into smaller pieces and add olive oil, salt and pepper. Mix well. Spray
  a standard size non-stick cupcake tin with cooking spray and spoon broccoli mixture evenly into 9 tins. In
  a medium bowl, beat egg whites, eggs, grated cheese, salt and pepper. Pour into the greased tins over
  broccoli until a little more than 3/4 full. Top with grated cheddar and bake in the oven until cooked, about
  20 minutes. Serve immediately. Wrap any leftovers in plastic wrap and store in the refrigerator to enjoy
  during the week.""";
  recipe22['ingredients'].append({'ingredient': u'broccoli', 'number': u'4 cup'})
  recipe22['ingredients'].append({'ingredient': u'eggs', 'number': u'4'})
  recipe22['ingredients'].append({'ingredient': u'egg whites', 'number': u'1 cup'})
  recipe22['ingredients'].append({'ingredient': u'cheddar', 'number': u'1/4 cup'})
  recipe22['ingredients'].append({'ingredient': u'pecorino romano', 'number': u'1/4 cup'})
  recipe22['ingredients'].append({'ingredient': u'olive oil', 'number': u'1 tablespoon'})
  recipe22['ingredients'].append({'ingredient': u'salt', 'number': u'1/2 teaspoon'})
  recipe22['ingredients'].append({'ingredient': u'pepper', 'number': u'1/2 teaspoon'})
  recipe22['tags'].append(u'breakfast')
  recipe22['tags'].append(u"vegetarian")
  recipe22['tags'].append(u"low-carb")
  recipe22['tags'].append(u"gluten-free")
  recipe22['tags'].append(u"salty")
  recipe22['serves'] = 4
  recipe22.save()

  recipe23 = recipecol.Recipe()
  recipe23['_id'] = 23
  recipe23['userid'] = u'filip'
  recipe23['title'] = u'Easy Taco Soup'
  recipe23['text'] = u"""Brown meat in large pan. Drain off excess grease and set aside. In same pot, sauté
  onions, bell pepper and zucchini for about 5-10 minutes or until soft. Add meat back to pan along with rest
  of ingredients. Cook on medium-low heat for 20 minutes. Taste for seasoning.
  Creamy Taco Soup:  Add 8 oz. cream cheese to soup and stir until melted.
  Crock Pot Method: Add cooked meat to crock pot along with rest of ingredients. Cook on low for 6 hours or
  high heat for 3 hours.""";
  recipe23['ingredients'].append({'ingredient': u'ground beef', 'number': u'1 kg'})
  recipe23['ingredients'].append({'ingredient': u'onion', 'number': u'1'})
  recipe23['ingredients'].append({'ingredient': u'bell pepper', 'number': u'1'})
  recipe23['ingredients'].append({'ingredient': u'zucchini', 'number': u'3'})
  recipe23['ingredients'].append({'ingredient': u'jalapeños', 'number': u'2'})
  recipe23['ingredients'].append({'ingredient': u'garlic', 'number': u'6 cloves'})
  recipe23['ingredients'].append({'ingredient': u'tomatoes', 'number': u'6'})
  recipe23['ingredients'].append({'ingredient': u'chicken stock', 'number': u'4 cup'})
  recipe23['ingredients'].append({'ingredient': u'taco Seasoning', 'number': u'1/4 cup'})
  recipe23['ingredients'].append({'ingredient': u'lime', 'number': u'2'})
  recipe23['tags'].append(u'paleo')
  recipe23['tags'].append(u"soup")
  recipe23['tags'].append(u"low-carb")
  recipe23['tags'].append(u"lunch")
  recipe23['tags'].append(u"mexican")
  recipe23['tags'].append(u"spicy")
  recipe23['tags'].append(u"low-cost")
  recipe23['serves'] = 8
  recipe23.save()

  recipe24 = recipecol.Recipe()
  recipe24['_id'] = 24
  recipe24['userid'] = u'qacer'
  recipe24['title'] = u'Portobello Mushroom Burgers'
  recipe24['text'] = u"""Place the mushroom caps, smooth side up, in a shallow dish. In a small bowl, whisk
  together vinegar, oil, basil, oregano, garlic, salt, and pepper. Pour over the mushrooms. Let stand at room
  temperature for 15 minutes or so, turning twice. Preheat grill for medium-high heat. Brush grate with oil.
  Place mushrooms on the grill, reserving marinade for basting. Grill for 5 to 8 minutes on each side, or until
  tender. Brush with marinade frequently. Top with cheese during the last 2 minutes of grilling.""";
  recipe24['ingredients'].append({'ingredient': u'portobello mushroom', 'number': u'4'})
  recipe24['ingredients'].append({'ingredient': u'balsamic vinegar', 'number': u'1/4 cup'})
  recipe24['ingredients'].append({'ingredient': u'olive oil', 'number': u'2 tablespoon'})
  recipe24['ingredients'].append({'ingredient': u'dried basil', 'number': u'1 teaspoon'})
  recipe24['ingredients'].append({'ingredient': u'dried oregano', 'number': u'1 teaspoon'})
  recipe24['ingredients'].append({'ingredient': u'garlic', 'number': u'2 cloves'})
  recipe24['ingredients'].append({'ingredient': u'provolone', 'number': u'100 g'})
  recipe24['ingredients'].append({'ingredient': u'salt', 'number': u'1/2 teaspoon'})
  recipe24['ingredients'].append({'ingredient': u'pepper', 'number': u'1/2 teaspoon'})
  recipe24['tags'].append(u"low-carb")
  recipe24['tags'].append(u"vegetarian")
  recipe24['tags'].append(u"dinner")
  recipe24['serves'] = 4
  recipe24.save()

  recipe25 = recipecol.Recipe()
  recipe25['_id'] = 25
  recipe25['userid'] = u'admin'
  recipe25['title'] = u'Pizza with Sweet Potato Crust'
  recipe25['text'] = u"""Cook sweet potatoes in a 400 degree oven for 50 minutes. Remove from heat, and once
  cooled, remove skin; (it should peel right off.) Mash sweet potatoes with a masher; you should yield about 2
  cups. Combine mashed sweet potatoes in a large bowl with quinoa flour, 2 tbsp. olive oil, and water. Mix
  thoroughly either in a food processor or knead with your hands to form dough. Roll dough into a circular
  pizza crust shape onto a nonstick pizza tray; (I made 1 large pizza, but you can make 2 or 3 smaller ones if
  you'd like.) Bake crust at 400 degrees for 10 minutes, then remove from heat. While the crust is baking, soak
  kale with lemon juice from your lemon. Stir remaining 2 tablespoons of olive oil with minced garlic, and
  spread evenly on baked crust. Distribute lemon marinated kale and tomatoes, and bake for additional 25
  minutes at 400 degrees. Once ready, remove from oven and let cool. Sprinkle with nutritional yeast, slice,
  and serve your gourmet pizza!""";
  recipe25['ingredients'].append({'ingredient': u'sweet potatoe', 'number': u'4'})
  recipe25['ingredients'].append({'ingredient': u'quinoa flour', 'number': u'2 1/2 cup'})
  recipe25['ingredients'].append({'ingredient': u'olive oil', 'number': u'4 tablespoon'})
  recipe25['ingredients'].append({'ingredient': u'water', 'number': u'1/4 cup'})
  recipe25['ingredients'].append({'ingredient': u'kale', 'number': u'1'})
  recipe25['ingredients'].append({'ingredient': u'tomatoes', 'number': u'5'})
  recipe25['ingredients'].append({'ingredient': u'lemon', 'number': u'1'})
  recipe25['ingredients'].append({'ingredient': u'garlic', 'number': u'2 cloves'})
  recipe25['ingredients'].append({'ingredient': u'nutritional yeast', 'number': u'1/4 cup'})
  recipe25['ingredients'].append({'ingredient': u'pepper', 'number': u'1/2 teaspoon'})
  recipe25['tags'].append(u"gluten-free")
  recipe25['tags'].append(u"vegan")
  recipe25['tags'].append(u"vegetarian")
  recipe25['tags'].append(u"paleo")
  recipe25['tags'].append(u"sweet")
  recipe25['tags'].append(u"vegetables")
  recipe25['serves'] = 10
  recipe25.save()



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
  user2['ratings'].append({'itemid':2,'value':4.0, 'date_creation': datetime.now()})
  user2['ratings'].append({'itemid':9,'value':4.0, 'date_creation': datetime.now()})
  user2['ratings'].append({'itemid':15,'value':5.0, 'date_creation': datetime.now()})
  user2['ratings'].append({'itemid':16,'value':2.0, 'date_creation': datetime.now()})
  user2['ratings'].append({'itemid':22,'value':3.0, 'date_creation': datetime.now()})
  user2['ratings'].append({'itemid':7,'value':1.0, 'date_creation': datetime.now()})
  user2['ratings'].append({'itemid':20,'value':1.0, 'date_creation': datetime.now()})
  user2['ratings'].append({'itemid':6,'value':2.0, 'date_creation': datetime.now()})
  user2.save()

  user3 = userscol.User()
  user3['_id'] = 'cospel'
  user3['fullname'] = u'Michal Lukac'
  user3['email'] = u'cospelthetraceur@gmail.com'
  user3['password'] = u'cospel'
  user3['ratings'].append({'itemid':4,'value':5.0, 'date_creation': datetime.now()})
  user3['ratings'].append({'itemid':13,'value':4.0, 'date_creation': datetime.now()})
  user3['ratings'].append({'itemid':25,'value':1.0, 'date_creation': datetime.now()})
  user3['ratings'].append({'itemid':2,'value':4.0, 'date_creation': datetime.now()})
  user3['ratings'].append({'itemid':2,'value':4.0, 'date_creation': datetime.now()})
  user3.save()

  user4 = userscol.User()
  user4['_id'] = 'qacer'
  user4['fullname'] = u'Jakub Kusnier'
  user4['email'] = u'qacer8@gmail.com'
  user4['password'] = u'qacer'
  user4['ratings'].append({'itemid':1,'value':3.0, 'date_creation': datetime.now()})
  user4['ratings'].append({'itemid':3,'value':5.0, 'date_creation': datetime.now()})
  user4['ratings'].append({'itemid':7,'value':3.0, 'date_creation': datetime.now()})
  user4['ratings'].append({'itemid':13,'value':4.0, 'date_creation': datetime.now()})
  user4['ratings'].append({'itemid':19,'value':2.0, 'date_creation': datetime.now()})
  user4['ratings'].append({'itemid':25,'value':4.0, 'date_creation': datetime.now()})
  user4.save()

  user5 = userscol.User()
  user5['_id'] = 'filip'
  user5['fullname'] = u'Filip Bu'
  user5['email'] = u'filip@bu.sk'
  user5['password'] = u'filip'
  user5['ratings'].append({'itemid':7,'value':5.0, 'date_creation': datetime.now()})
  user5['ratings'].append({'itemid':11,'value':4.0, 'date_creation': datetime.now()})
  user5['ratings'].append({'itemid':1,'value':4.5, 'date_creation': datetime.now()})
  user5['ratings'].append({'itemid':3,'value':4.0, 'date_creation': datetime.now()})
  user5['ratings'].append({'itemid':20,'value':5.0, 'date_creation': datetime.now()})
  user5['ratings'].append({'itemid':16,'value':1.0, 'date_creation': datetime.now()})
  user5.save()

  user6 = userscol.User()
  user6['_id'] = 'radek'
  user6['fullname'] = u'Radek Pelanek'
  user6['email'] = u'xpelanek@fi.muni.cz'
  user6['password'] = u'radek'
  user6.save()


if __name__ == '__main__':
  pass