from sqlalchemy.orm import Session
from fastapi import HTTPException
from data.schema.schemas import UserCreate, UserProfileUpdate, FoodCategoryCreate
from data.model.models import User, FoodCategory
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


def create_food_category(db: Session, category: FoodCategoryCreate, current_user: User):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can add food categories")

    new_category = FoodCategory(
        name=category.name,
        image_url=category.image_url,
        is_active=category.is_active
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

