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
    recipe = Recipe(1, 'admin', 'Mixed eggs', """I wish you'd have given me this written question ahead of time so I
    could plan for it... I'm sure something will pop into my head here in
    the midst of this press conference, with all the pressure of trying to
    come up with answer, but it hadn't yet... I don't want to sound like
    I have made no mistakes. I'm confident I have. I just haven't - you
    just put me under the spot here, and maybe I'm not as quick on my feet
    as I should be in coming up with one.""", 'paleo,raw', None)
    recipe2 = Recipe(2, 'collfi', 'Honey rice', """I wish you'd have given me this written question ahead of time so I
    could plan for it... I'm sure something will pop into my head here in
    the midst of this press conference, with all the pressure of trying to
    come up with answer, but it hadn't yet... I don't want to sound like
    I have made no mistakes. I'm confident I have. I just haven't - you
    just put me under the spot here, and maybe I'm not as quick on my feet
    as I should be in coming up with one.""", 'vegan,raw', None)
    recipe3 = Recipe(3, 'collfi', 'Roasted beef with chips', """I wish you'd have given me this written question ahead of time so I
    could plan for it... I'm sure something will pop into my head here in
    the midst of this press conference, with all the pressure of trying to
    come up with answer, but it hadn't yet... I don't want to sound like
    I have made no mistakes. I'm confident I have. I just haven't - you
    just put me under the spot here, and maybe I'm not as quick on my feet
    as I should be in coming up with one.""", 'unhealthy,fat',None)
    db_session.add(recipe)
    db_session.add(recipe2)
    db_session.add(recipe3)
    db_session.commit()
