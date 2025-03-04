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

    # Relationship
    food_menus = relationship("FoodMenu", back_populates="owner")
    cart_items = relationship("Cart", back_populates="user")
    # orders = relationship("Order", back_populates="food")

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

    # Relationship
    owner = relationship("User", back_populates="food_menus")
    cart_items = relationship("Cart", back_populates="food")
    # orders = relationship("Order", back_populates="food")

    def __repr__(self):
        return f"<Food(food_name={self.food_name}, price={self.price})>"


class Cart(Base):
    __tablename__ = "cart"

    cart_id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("food_menu.food_id"), nullable=False)
    food_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    # Relationships
    user = relationship("User", back_populates="cart_items")
    food = relationship("FoodMenu", back_populates="cart_items")

    def __repr__(self):
        return (f"<Cart(cart_id={self.cart_id}, food_name={self.food_name}, "
                f"quantity={self.quantity}, price={self.price})>")


# class OrderFood(Base):
#     __tablename__ = "orders"
#
#     order_no = Column(Integer, primary_key=True, index=True)
#     food_id = Column(Integer, ForeignKey("food_menu.food_id"), nullable=False)
#     food_name = Column(String, nullable=False)
#     quantity = Column(Integer, nullable=False)
#     user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
#     user_fullname = Column(String, nullable=False)
#     status = Column(String, default="Pending")
#     order_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
#     total_price = Column(Float, nullable=False)
#
#     # Relationships
#     user = relationship("User", back_populates="orders")
#     food = relationship("FoodMenu", back_populates="orders")
#
#     def __repr__(self):
#         return (f"<Order(order_no={self.order_no}, food_name={self.food_name}, "
#                 f"quantity={self.quantity}, total_price={self.total_price})>")