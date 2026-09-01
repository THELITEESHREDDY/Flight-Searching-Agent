from sqlalchemy import Column,String
from utils.db import base

class UserTable(base):
    __tablename__ = "Users"

    id= Column(String,primary_key=True)
    email= Column(String)
    hashed_password =Column(String)
