from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from data.database import SessionLocal
from auth import create_access_token, get_current_user
from data.curd import create_user, get_user_by_username, verify_password
from data.schema.schemas import UserCreate, TokenResponse, UserLogin
from data.model.models import User
from swagger_config import custom_openapi  # Import the custom Swagger configuration

app = FastAPI()

# Apply the custom Swagger configuration
app.openapi = lambda: custom_openapi(app)


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Signup Endpoint (Public Route)
@app.post("/user/create", response_model=TokenResponse)
def create_user_api(user: UserCreate, db: Session = Depends(get_db)):
    try:
        created_user = create_user(db, user)
    except HTTPException as e:
        raise e

    access_token = create_access_token(data={"sub": created_user.user_name})
    return {"access_token": access_token, "token_type": "bearer"}


# Login Endpoint
@app.post("/login", response_model=TokenResponse)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_username(db, login_data.user_name)
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": user.user_name})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Welcome to my restaurant"
    }


# Protected Route
@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "user_name": current_user.user_name,
        "fullname": current_user.fullname,
        "email": current_user.email,
        "address": current_user.address,
        "phone_no": current_user.phone_no,
        "post_code": current_user.post_code,
        "role": current_user.role,
        "created_date": current_user.created_date
    }
