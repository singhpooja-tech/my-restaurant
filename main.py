from fastapi import FastAPI, Depends
from sqlalchemy import func
from data.database import *
from auth import create_access_token, get_current_user
from data.curd import *
from data.schema.schemas import *
from data.model.models import User, FoodMenu
from typing import List
from swagger_config import custom_openapi  # Import the custom Swagger configuration
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="templates/images/menu"), name="static")

# Apply the custom Swagger configuration
app.openapi = lambda: custom_openapi(app)


# Function to create all tables automatically
def create_tables():
    Base.metadata.create_all(bind=engine)  # Recreates tables with new schema


# Call create_tables once during application start
create_tables()


# Signup Endpoint (Public Route)
@app.post("/user/register", summary=" ", response_model=TokenSignupResponse, tags=["Authentication"])
def create_user_api(user: UserCreate, db: Session = Depends(get_db)):
    try:
        create_user(db, user)
    except HTTPException as e:
        raise e
    # access_token = create_access_token(data={"sub": created_user.user_name})
    return {
        "message": "successful registration",
        "token_type": "bearer"
    }


# Login Endpoint
@app.post("/ welcome message", summary="After Login", response_model=TokenLoginResponse, tags=["Authentication"])
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
@app.get("/me", summary="Current User Info", response_model=UserInformation, tags=["user_information"])
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
@app.put("/me/update", summary="Update Current User Info", response_model=UserProfileUpdateResponse, tags=["user_information"])
def get_updated_user(user_update: UserProfileUpdate,
                     current_user: User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    if current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Admins are not authorized to update user data")

    updated_user = update_user_info(db, current_user.user_id, user_update)
    return {
        "msg": "user profile is updated"
    }


# Create Restaurant Menu(Only Admin Can DO)
@app.post("/menu/add", summary="Add New Food Item", response_model=CreateFoodMenuResponse, tags=["admin_dashboard"])
def create_restaurant_food_menu(menu: CreateFoodMenu,
                                db: Session = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    if current_user.role == "user":
        raise HTTPException(status_code=403, detail="User are not Authorized to Add Food Menu")

    create_food_menu(db, current_user.user_id, menu)
    return {
        "message": "Food Item Successfully Added in Restaurant Food Menu"
    }


# update Food  Menu Item
@app.put("/menu/update", summary="Update Food Item by ID", tags=["admin_dashboard"])
def update_food_menu(food_id: int, food_update: FoodMenuUpdate,
                     current_user: User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    if current_user.role == "user":
        raise HTTPException(status_code=403, detail="User are not authorized to update Menu")

    update_food_menu_by_id(db, food_id, food_update)
    return {
        "message": "Food menu updated successfully",

    }


# Delete Food  Menu Item
@app.delete("/menu/delete/", summary="Delete Food Item by ID", tags=["admin_dashboard"])
def delete_food_menu(food_id: int,
                     current_user: User = Depends(get_current_user),
                     db: Session = Depends(get_db)):

    if current_user.role == "user":
        raise HTTPException(status_code=403, detail="User is not authorized to delete Menu")

    delete_food_menu_by_id(db, food_id)
    return {
        "message": "Food menu Deleted successfully According to Given Food ID",
    }


# Get Menu Item
@app.get("/menu", summary=" ", response_model=List[GetFoodMenuResponse], tags=["user_dashboard"])
def get_restaurant_menu(db: Session = Depends(get_db)):
    """
        Get All the current Food Menu.
    """
    menu = db.query(FoodMenu).all()
    # Return the image URL as a string (no markdown or HTML)
    return [{
        "food_id": food.food_id,
        "food_name": food.food_name,
        "quantity": food.quantity,
        "description": food.description,
        "category": food.category,
        "price": food.price,
        "food_image_url": f"http://localhost:8000{food.food_image_url}"  # Just a plain URL
    } for food in menu]


# Add Food Item In Cart(User Only)
@app.post("/select_food", summary="Add Food In Cart", tags=["user_dashboard"])
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
@app.get("/cart", summary=" ", response_model=CartResponse, tags=["user_dashboard"])
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


@app.post("/order", summary="Place Order", tags=["user_dashboard"])
def place_order_api(db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Only users can place orders.")

    return place_order(db, current_user.user_id)


# @app.get("/admin/orders-by-date", tags=["Admin"])
# def get_orders_by_date_api(start_date: datetime,
#                            end_date: datetime,
#                            db: Session = Depends(get_db),
#                            current_user: User = Depends(get_current_user)):
#
#     # Check if the current user is an admin
#     if current_user.role == "user":
#         raise HTTPException(status_code=403, detail="Only admins can Check Orders.")
#
#     # Fetch orders data
#     orders = get_orders_by_date(db, start_date, end_date)
#
#     return {"orders": orders}
@app.get("/orders/?sortBy='date'", summary=" ", tags=["admin_dashboard"])
def get_orders(start_date: str, end_date: str, db: Session = Depends(get_db)):

    try:
        # Convert date strings to datetime objects
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Validate date range
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Start date must be before end date.")

        # Call the function from crud.py to get orders in the date range
        grouped_orders = get_orders_by_date(db, start_date, end_date)

        # Prepare response
        response_data = {
            "no_of_orders": len(grouped_orders),
            "orders": list(grouped_orders.values())
        }
        return response_data

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")


@app.post("/feedback/", summary="Create Feedback and Rating", tags=["user_dashboard"])
def create_feedback_endpoint(feedback: CreateFeedback,
                             db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):

    # Check if the user is authorized to give feedback (you can modify role validation as needed)
    if current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Admin cannot submit feedback")

    # Call the CRUD function to store feedback
    new_feedback = create_feedback(db, current_user.user_id, current_user.fullname, feedback)

    return {
        "message": "Feedback submitted successfully",
        "feedback": new_feedback
    }


@app.get("/feedbacks/", summary="Get All Feedbacks of User", tags=["admin_dashboard"])
def get_all_feedback_endpoint(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view all feedback")

    # Fetch all feedback using the CRUD function
    feedback_list = get_all_feedback(db)
    return {"feedback": feedback_list}
