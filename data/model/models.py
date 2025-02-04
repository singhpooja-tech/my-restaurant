from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from data.database import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, nullable=True)
    user_name = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    address = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    phone_no = Column(String, nullable=True)  # Changed to string
    created_date = Column(DateTime, default=datetime.utcnow)
    post_code = Column(Integer, nullable=True)
    role = Column(String, default="user")