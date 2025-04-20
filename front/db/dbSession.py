from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URI = os.getenv('DATABASE_URI')

engine = create_engine(DATABASE_URI)

Session = sessionmaker(bind=engine)
session = Session()