from sqlalchemy import Column, Integer, String, DateTime, Text, LargeBinary, Boolean
from datetime import datetime, timezone
from data.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, nullable=True)
    user_name = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    address = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    phone_no = Column(Text, nullable=True)
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    post_code = Column(Integer, nullable=True)
    role = Column(String, default="user", server_default="user")

    def __repr__(self):
        return f"<User(user_name={self.user_name}, email={self.email})>"


class FoodCategory(Base):
    __tablename__ = "food_category"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    image_url = Column(LargeBinary, nullable=True)  # Stores image data as binary
    is_active = Column(Boolean, nullable=False, server_default="1")  # Maps 'Y'/'N' to True/False
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # Auto timestamp

    def __repr__(self):
        return f"<FoodCategory(name={self.name}, is_active={self.is_active})>"

