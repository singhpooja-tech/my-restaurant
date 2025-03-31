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

    food_menus = relationship("FoodMenu", back_populates="user")
    carts = relationship("Cart", back_populates="user")
    orders = relationship("Orders", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(user_name={self.user_name}, email={self.email})>"


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    image_url = Column(String, nullable=True)
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    food_menus = relationship("FoodMenu", back_populates="category", cascade="all, delete", passive_deletes=True)

    def __repr__(self):
        return f"<Category(name={self.name})>"


class FoodMenu(Base):
    __tablename__ = "food_menu"

    food_id = Column(Integer, primary_key=True, index=True)
    food_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="CASCADE"), nullable=False)
    category_name = Column(String, nullable=False)
    is_active = Column(String, default="Yes")
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    price = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    food_image_url = Column(String, nullable=True)

    category = relationship("Category", back_populates="food_menus")
    user = relationship("User", back_populates="food_menus")
    carts = relationship("Cart", back_populates="food")
    order_items = relationship("OrderItem", back_populates="food", cascade="all, delete-orphan")

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

    user = relationship("User", back_populates="carts")
    food = relationship("FoodMenu", back_populates="carts")

    def __repr__(self):
        return (f"<Cart(cart_id={self.cart_id}, food_name={self.food_name}, "
                f"quantity={self.quantity}, price={self.price})>")


class Orders(Base):
    __tablename__ = "orders"

    order_no = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    status = Column(String, default="Pending")
    order_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    total_price = Column(Float, nullable=False)

    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(order_no={self.order_no}, status={self.status}, total_price={self.total_price})>"


class OrderItem(Base):
    __tablename__ = "order_item"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_no = Column(Integer, ForeignKey("orders.order_no"), nullable=False)
    food_id = Column(Integer, ForeignKey("food_menu.food_id", ondelete="CASCADE"), nullable=False)
    food_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)

    order = relationship("Orders", back_populates="order_items")
    food = relationship("FoodMenu", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem(order_no={self.order_no}, food_name={self.food_name}, quantity={self.quantity})>"


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    rating = Column(Float, nullable=True)

    user = relationship("User", back_populates="feedbacks")

    def __repr__(self):
        return f"<Feedback(user_id={self.user_id}, rating={self.rating})>"


