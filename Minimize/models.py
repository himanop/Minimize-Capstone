from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

# Example of creating an engine and session
DATABASE_URL = "postgresql://username:password@localhost/dbname"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Create all tables
Base.metadata.create_all(engine)