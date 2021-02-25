from flask_sqlalchemy import BaseQuery
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from .config import Config

config = Config()

engine = create_engine(config.DATABASE_URI, **config.db_engine_config)
db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property(query_cls=BaseQuery)

