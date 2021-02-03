from sqlalchemy import Column, Integer, DateTime, String, Boolean
from sqlalchemy.sql import func

from .exts import db

class User(db.Model):
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, server_default=func.now())
    apikey = Column(String(64), unique=True)
    desc = Column(String(100))

class Binary(db.Model):
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, server_default=func.now())
    requestor = Column(String(50))
    status = Column(Boolean)
    output_dir = Column(String(20))
