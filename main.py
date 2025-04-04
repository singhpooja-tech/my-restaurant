from fastapi import FastAPI, Depends
from sqlalchemy import func
from data.database import *
from auth import create_access_token, get_current_user
from data.curd import *
from data.schema.schemas import *
from data.model.models import *
from typing import List
from swagger_config import custom_openapi  # Import the custom Swagger configuration
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/menu_images", StaticFiles(directory="templates/images/menu"), name="menu_images")
app.mount("/category_images", StaticFiles(directory="templates/images/category"), name="category_images")


@app.get("/", summary="Welcome Message", tags=["Home"])
def home():
    return {"message": "Welcome to my FastAPI restaurant app!"}


# Apply the custom Swagger configuration
app.openapi = lambda: custom_openapi(app)


# Function to create all tables automatically
def create_tables():
    Base.metadata.create_all(bind=engine)  # Recreates tables with new schema


# Call create_tables once during application start
create_tables()


# Signup Endpoint (Public Route)
@app.post("/register", summary="Create Account", response_model=TokenSignupResponse, tags=["Authentication"])
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
@app.post("/login", summary="Get Token Message", response_model=TokenLoginResponse, tags=["Authentication"])
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
@app.get("/me", summary="Current User Info", response_model=UserInformation, tags=["user"])
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
@app.put("/me/update", summary="Update Current User Info", response_model=UserProfileUpdateResponse,
         tags=["user"])
def get_updated_user(user_update: UserProfileUpdate,
                     current_user: User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    if current_user.role == "admin":
        raise HTTPException(status_code=403, detail="Admins are not authorized to update user data")

    updated_user = update_user_info(db, current_user.user_id, user_update)
    return {
        "msg": "user profile is updated"
    }


# Create Category(Only Admin Can DO)
@app.post("/category", summary="Add Category Item (Admin)", response_model=UserProfileUpdateResponse, tags=["menu"])
def create_food_category(category: CreateCategoryRequest,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    create_category(db, current_user.user_id, category)
    return {
        "msg": "Item Successfully Added in Category"
    }


# Get All Category(Admin & User)
@app.get("/category", summary="Get all category Item (Admin & User) ", response_model=List[CreateCategory],
         tags=["menu"])
def get_category(db: Session = Depends(get_db)):

    """

        Get All the current Food Menu.

    """
    category = db.query(Category).all()
    # Return the image URL as a string (no markdown or HTML)
    return [{
        "category_id": food.category_id,
        "name": food.name,
        "image_url": f"http://localhost:8000/{food.image_url}"  # Just a plain URL
    } for food in category]


@app.delete("/category/{id}", summary="Delete category Item (Admin)", tags=["menu"])
def delete_category_item(category_id: int,
                         current_user: User = Depends(get_current_user),
                         db: Session = Depends(get_db)):

    if current_user.role == "user":
        raise HTTPException(status_code=403, detail="User is not authorized to delete Menu")

    delete_category_by_id(db, category_id)
    return {
        "message": "Category Deleted successfully According to Given ID",
    }


# update Category Item
@app.put("/category/{id}", summary="Update Category Item (Admin)", tags=["menu"])
def update_category_item(food_id: int, category_update: UpdateCategory,
                         current_user: User = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if current_user.role == "user":
        raise HTTPException(status_code=403, detail="User are not authorized to update Menu")

    update_category_by_id(db, food_id, category_update)
    return {
        "message": "Food menu updated successfully",

    }


# Create Restaurant Menu(Only Admin Can DO)
@app.post("/menu", summary="Add New Menu Item (Admin)", response_model=CreateFoodMenuResponse, tags=["menu"])
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
@app.put("/menu/{id}", summary="Update Menu Item (Admin)", tags=["menu"])
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
@app.delete("/menu/{id}", summary="Delete Menu Item (Admin)", tags=["menu"])
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
@app.get("/menu/{Category}", summary="Get all Menu Item by Category (Admin & User) ",
         response_model=List[GetFoodMenuResponse], tags=["menu"])
def get_restaurant_menu(category_name: str = "All", db: Session = Depends(get_db)):
    """
    Get all the current Food Menu according category_name
    """
    if category_name == "All":
        # If category_name is 'All', get all the menu items
        menu = db.query(FoodMenu).all()
    else:
        # Otherwise, filter by category_name
        category = db.query(Category).filter(Category.name == category_name).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        menu = db.query(FoodMenu).filter(FoodMenu.category_name == category_name).all()

    # Return the food menu data with image URLs
    return [{
        "food_id": food.food_id,
        "food_name": food.food_name,
        "quantity": food.quantity,
        "description": food.description,
        "category_id": food.category_id,
        "category_name": food.category_name,
        "price": food.price,
        "food_image_url": f"http://localhost:8000/{food.food_image_url}"  # Just a plain URL
    } for food in menu]


# Add Food Item In Cart(User Only)
@app.post("/select_food/{id}", summary="Add Food Item In Cart (User)", tags=["cart"])
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
@app.get("/cart", summary="All Selected Food Item in Cart ", response_model=CartResponse, tags=["cart"])
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


@app.post("/order", summary="Place Order (User)", tags=["order"])
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
@app.get("/orders/{date}", summary="Get All Orders According to Date (Admin)  ", tags=["order"])
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


@app.post("/feedback", summary="Create Feedback (User)", tags=["order"])
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


@app.get("/feedbacks", summary="Get All Feedbacks (Admin)", tags=["order"])
def get_all_feedback_endpoint(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view all feedback")

    # Fetch all feedback using the CRUD function
    feedback_list = get_all_feedback(db)
    return {"feedback": feedback_list}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
