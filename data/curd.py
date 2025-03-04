from sqlalchemy.orm import Session
from fastapi import HTTPException
from data.schema.schemas import UserCreate, UserProfileUpdate, CreateFoodMenu, AddToCart
from data.model.models import User, FoodMenu, Cart
from passlib.context import CryptContext

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash("pooja123456")
print(hashed_password)


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
        user_id=user_id  # Ensure this is an integer
    )

    db.add(menu)
    db.commit()
    db.refresh(menu)
    return menu


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
