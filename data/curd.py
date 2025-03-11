from collections import defaultdict
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi import HTTPException
from data.schema.schemas import *
from data.model.models import *
from passlib.context import CryptContext

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# hashed_password = pwd_context.hash("pooja123456")
# print(hashed_password)


def hash_password(password: str):
    return pwd_context.hash(password)


# Verify if the provided password matches the hashed password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Function to create a new user
def create_user(db: Session, user: UserCreate):
    # Check if username already exists
    if db.query(User).filter(User.user_name == user.user_name).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = hash_password(user.password)  # Hash the password
    db_user = User(
        fullname=user.fullname,
        user_name=user.user_name,
        email=user.email,
        password=hashed_password,
        phone_no=user.phone_no  # Only use phone_no as it exists in UserCreate
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Function to get a user by username
def get_user_by_username(db: Session, user_name: str):
    user = db.query(User).filter(User.user_name == user_name).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


# Function to update user information according role
def update_user_info(db: Session, user_id: int, user_update: UserProfileUpdate):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update only provided fields (using model_dump instead of dict)
    update_data = user_update.model_dump(exclude_unset=True)  # Pydantic v2

    for key, value in update_data.items():
        setattr(user, key, value)  # Dynamically update fields

    db.commit()  # Save changes
    db.refresh(user)  # Refresh to get updated values
    return user


# Function to Create Restaurant Food Menu
def create_food_menu(db: Session, user_id: int, food_menu: CreateFoodMenu):
    if db.query(FoodMenu).filter(FoodMenu.food_name == food_menu.food_name).first():
        raise HTTPException(status_code=400, detail="This Food is already in menu")

    menu = FoodMenu(
        food_name=food_menu.food_name,
        description=food_menu.description,
        quantity=food_menu.quantity,
        category=food_menu.category,
        is_active=food_menu.is_active,
        price=food_menu.price,
        food_image_url=food_menu.food_image_url,
        user_id=user_id  # Ensure this is an integer
    )

    db.add(menu)
    db.commit()
    db.refresh(menu)
    return menu


# Function to Update Restaurant Food Menu Based On Given Food ID
def update_food_menu_by_id(db: Session, food_id: int, food_menu: FoodMenuUpdate):
    food = db.query(FoodMenu).filter(FoodMenu.food_id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="food not found")
    update_food = food_menu.model_dump(exclude_unset=True)
    for key, value in update_food.items():
        setattr(food, key, value)

    db.commit()
    db.refresh(food)
    return food


# Function to Delete Restaurant Food Menu Based On Given Food ID
def delete_food_menu_by_id(db: Session, food_id: int):
    food = db.query(FoodMenu).filter(FoodMenu.food_id == food_id).first()

    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    db.delete(food)  # Delete the food entry from the database
    db.commit()  # Commit the transaction


# Function to Add Food Item InTo Cart
def add_to_cart(db: Session, user_id: int, cart_data: AddToCart):
    # Fetch food details
    food_item = db.query(FoodMenu).filter(FoodMenu.food_id == cart_data.food_id).first()

    if not food_item:
        raise HTTPException(status_code=404, detail="Food item not found")

    if cart_data.quantity > food_item.quantity:
        raise HTTPException(status_code=400, detail="Not enough quantity available")

    total_price = cart_data.quantity * food_item.price  # Calculate total price

    # Create cart item
    cart_item = Cart(
        food_id=food_item.food_id,
        food_name=food_item.food_name,
        quantity=cart_data.quantity,
        price=food_item.price,
        total_price=total_price,  # Store calculated total price
        user_id=user_id
    )

    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item


def place_order(db: Session, user_id: int):
    # Fetch cart items for the user
    cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty. Cannot place order.")

    # Get the last order number and increment it
    last_order = db.query(Orders).order_by(Orders.order_no.desc()).first()
    order_no = last_order.order_no + 1 if last_order else 1  # Start from 1

    # Calculate total order price
    total_price = sum(item.total_price for item in cart_items)

    try:
        # Create a new order record
        new_order = Orders(
            order_no=order_no,
            user_id=user_id,
            status="Completed",
            order_date=datetime.now(timezone.utc),
            total_price=total_price
        )
        db.add(new_order)
        db.flush()  # Flush to get the order ID before committing

        # Move cart items to the order_items table
        for item in cart_items:
            order_item = OrderItem(
                order_no=new_order.order_no,
                food_id=item.food_id,
                food_name=item.food_name,
                quantity=item.quantity,
            )
            db.add(order_item)
            # Decrease the food quantity in the menu
            food_item = db.query(FoodMenu).filter(FoodMenu.food_id == item.food_id).first()
            if food_item:
                if food_item.quantity < item.quantity:
                    raise HTTPException(status_code=400, detail=f"Not enough stock for {food_item.food_name}.")
                food_item.quantity -= item.quantity  # Deduct ordered quantity
                db.add(food_item)

        # Delete all cart items for the user
        db.query(Cart).filter(Cart.user_id == user_id).delete()
        db.commit()

        return {"message": "Order placed successfully!", "order_no": order_no, "total_price": total_price}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def get_orders_by_date(db: Session, start_date, end_date):
    # Fetch orders within the date range
    orders_data = db.query(
        Orders.order_no,
        Orders.total_price,
        OrderItem.food_id,
        OrderItem.food_name,
        OrderItem.quantity
    ).join(OrderItem).filter(
        Orders.order_date >= start_date,
        Orders.order_date <= end_date
    ).all()

    # Group orders by order_no
    grouped_orders = defaultdict(lambda: {"order_no": None, "total_price": 0, "items": []})

    for order in orders_data:
        order_no = order.order_no
        total_price = order.total_price
        food_id = order.food_id
        food_name = order.food_name
        quantity = order.quantity

        grouped_orders[order_no]["order_no"] = order_no
        grouped_orders[order_no]["total_price"] = total_price
        grouped_orders[order_no]["items"].append({
            "food_id": food_id,
            "food_name": food_name,
            "quantity": quantity
        })

    return grouped_orders


def create_feedback(db: Session, user_id: int, fullname: str, feedback: CreateFeedback):
    """Create a feedback entry with the logged-in user's ID"""
    new_feedback = Feedback(
        user_id=user_id,
        name=fullname,
        message=feedback.message,
        rating=feedback.rating
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback


def get_all_feedback(db: Session):
    """Fetch all feedback from the database"""
    return db.query(Feedback).all()
