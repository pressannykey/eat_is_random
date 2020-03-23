from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///tmp.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()
