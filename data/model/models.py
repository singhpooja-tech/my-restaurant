from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
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

    # Relationship to FoodMenu
    food_menus = relationship("FoodMenu", back_populates="owner")

    def __repr__(self):
        return f"<User(user_name={self.user_name}, email={self.email})>"


class FoodMenu(Base):
    __tablename__ = "food_menu"

    food_id = Column(Integer, primary_key=True, index=True)
    food_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    is_active = Column(String, default="Yes")
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    price = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"))

    # Relationship to User
    owner = relationship("User", back_populates="food_menus")

    def __repr__(self):
        return f"<Food(food_name={self.food_name}, price={self.price})>"

