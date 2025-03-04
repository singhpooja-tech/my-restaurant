from fastapi import FastAPI, Depends
from sqlalchemy import func
from data.database import *
from auth import create_access_token, get_current_user
from data.curd import *
from data.schema.schemas import *
from data.model.models import User, FoodMenu
from typing import List
from swagger_config import custom_openapi  # Import the custom Swagger configuration

app = FastAPI()

# Apply the custom Swagger configuration
app.openapi = lambda: custom_openapi(app)


# Function to create all tables automatically
def create_tables():
    Base.metadata.create_all(bind=engine)  # Recreates tables with new schema


# Call create_tables once during application start
create_tables()


# Signup Endpoint (Public Route)
@app.post("/user/create", response_model=TokenSignupResponse)
def create_user_api(user: UserCreate, db: Session = Depends(get_db)):
    try:
        created_user = create_user(db, user)
    except HTTPException as e:
        raise e
    # access_token = create_access_token(data={"sub": created_user.user_name})
    return {
        "message": "successful registration",
        "token_type": "bearer"
    }


# Login Endpoint
@app.post("/login", response_model=TokenLoginResponse)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_username(db, login_data.user_name)
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.user_name, "role": user.role})  # Include role in token
    return {
        "access_token": access_token,
        "message": "Welcome to my restaurant"
    }


# Protected Route
@app.get("/me", response_model=UserInformation)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get the current user's information.
    Requires a valid JWT token for authentication.
    """
    return {
        "fullname": current_user.fullname,
        "user_name": current_user.user_name,
        "email": current_user.email,
        "phone_no": current_user.phone_no,
        "address": current_user.address,
        "post_code": current_user.post_code,
        "role": current_user.role,
        "created_date": current_user.created_date
    }


# Update Current User (Admins cannot update users)
@app.put("/me/update", response_model=UserInformation)
def get_updated_user(user_update: UserProfileUpdate,
                     current_user: User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    if current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Admins are not authorized to update user data")

    updated_user = update_user_info(db, current_user.user_id, user_update)
    return {
        "fullname": updated_user.fullname,
        "user_name": updated_user.user_name,
        "email": updated_user.email,
        "phone_no": updated_user.phone_no,
        "address": updated_user.address,
        "post_code": updated_user.post_code,
        "role": updated_user.role,
        "created_date": updated_user.created_date
    }


# Create Restaurant Menu(Only Admin Can DO)
@app.post("/food_menu/add", response_model=CreateFoodMenuResponse)
def create_restaurant_food_menu(menu: CreateFoodMenu,
                                db: Session = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    if current_user.role == "user":
        raise HTTPException(status_code=403, detail="User are not Authorized to Add Food Menu")

    create_food_menu(db, current_user.user_id, menu)
    return {
        "message": "Food Item Successfully Added in Restaurant Food Menu"

    }


# Get Menu Item
@app.get("/get_food_menu", response_model=List[GetFoodMenuResponse])
def get_restaurant_menu(db: Session = Depends(get_db)):
    """
        Get All the current Food Menu.
    """
    menu = db.query(FoodMenu).all()
    return menu


# Add Food Item In Cart(User Only)
@app.post("/cart/add")
def add_item_to_cart(cart_data: AddToCart,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Only User Can Add Item")

    cart_item = add_to_cart(db, current_user.user_id, cart_data)
    return {
        "message": f"{cart_item.food_name} added to cart successfully",
        "total_price": cart_item.total_price
    }


# Get Cart Item
@app.get("/cart", response_model=CartResponse)
def view_cart(db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Only User Can see Item")

    # Get all cart items for the current user
    cart_items = db.query(Cart).filter(Cart.user_id == current_user.user_id).all()

    # Calculate the total price by summing up the 'total_price' column for all items
    total_price = db.query(func.sum(Cart.total_price)).filter(Cart.user_id == current_user.user_id).scalar()

    # Return cart items along with the total price
    return {
        "cart_items": cart_items,
        "total_price": total_price if total_price else 0.0  # Return 0 if no items are in the cart
    }
