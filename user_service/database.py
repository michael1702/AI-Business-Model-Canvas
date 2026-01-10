from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import os
from sqlalchemy import create_engine


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)