from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:////tmp/recsys.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from models import User, Recipe
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    user = User('admin', 'admin', 'cospelthetraceur@gmail.com', 'admin')
    user2 = User('collfi', 'collfi', 'collfi@collfi.sk', 'collfi')
    user3 = User('cospel', 'cospel', 'cospel@cospel.sk', 'cospel')
    db_session.add(user)
    db_session.add(user2)
    db_session.add(user3)
    db_session.commit()
    recipe = Recipe(1, 'admin', 'prazenica', 'postup', 'tag1,tag2', None)
    recipe2 = Recipe(2, 'collfi', 'ryza', 'postup', 'tag1,tag2', None)
    recipe3 = Recipe(3, 'collfi', 'dobrota', 'postup, postup;', 'tag2, tag3, tag4',None)
    db_session.add(recipe)
    db_session.add(recipe2)
    db_session.add(recipe3)
    db_session.commit()
