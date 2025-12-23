# group_service/database.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Define a separate Base specifically for Group models
class Base(DeclarativeBase):
    pass

# Create a distinct SQLAlchemy object for Group Service
db = SQLAlchemy(model_class=Base)