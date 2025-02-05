from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from data.database import SessionLocal
from auth import create_access_token, get_current_user
from data.curd import create_user, get_user_by_username, verify_password
from data.schema.schemas import UserCreate, TokenResponse
from fastapi.security import OAuth2PasswordRequestForm
from data.model.models import User

app = FastAPI()


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Signup Endpoint (Creates User & Returns JWT Token)
@app.post("/user/create", response_model=TokenResponse)
def create_user_api(user: UserCreate, db: Session = Depends(get_db)):
    try:
        created_user = create_user(db, user)  # Calls create_user from `curd.py`
    except HTTPException as e:
        raise e

    # Generate a JWT token for the new user
    access_token = create_access_token(data={"sub": created_user.user_name})
    return {"access_token": access_token, "token_type": "bearer"}


# Login Endpoint (Authenticates User & Returns JWT Token)
@app.post("/login", response_model=TokenResponse)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    # Generate JWT token
    access_token = create_access_token(data={"sub": user.user_name})
    return {"access_token": access_token, "token_type": "bearer"}


# Protected Endpoint (Fetches User Info Based on JWT Token)
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


