from pydantic import BaseModel, EmailStr, constr, field_validator
from typing import Optional
from datetime import datetime
from typing import List


# User Signup Schema
class UserCreate(BaseModel):
    fullname: str
    user_name: str
    email: EmailStr
    password: constr(min_length=6)  # Password must be at least 6 characters long
    phone_no: Optional[str] = None  # Changed to string for flexibility

    @field_validator("phone_no")
    def validate_phone(cls, v):
        if v and len(v) < 10:
            raise ValueError("Phone number must be at least 10 characters long.")
        elif v and len(v) > 10:
            raise ValueError("Phone number must be 10 characters long.")
        return v

    # @field_validator("post_code")
    # def validate_post_code(cls, v):
    #     if v and len(str(v)) < 5:
    #         raise ValueError("Post code must be at least 5 digits long.")
    #     return v


class UserLogin(BaseModel):
    user_name: str
    password: constr(min_length=6)  # Password must be at least 6 characters long


# JWT Token Response Schema
class TokenLoginResponse(BaseModel):
    access_token: str
    message: str


class TokenSignupResponse(BaseModel):
    message: str
    token_type: str


# JWT get user profile Token Response Schema
class UserInformation(BaseModel):
    fullname: str
    user_name: str
    email: EmailStr
    phone_no: str
    address: str | None
    post_code: int | None
    role: str
    created_date: datetime


# JWT get updated user profile Token Response Schema
class UserProfileUpdate(BaseModel):
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_no: Optional[str] = None
    address: Optional[str] = None
    post_code: Optional[int] = None


# Create Restaurant Menu
class CreateFoodMenu(BaseModel):
    food_name: str
    description: str | None
    quantity: int
    category: str
    is_active: str
    price: float


class CreateFoodMenuResponse(BaseModel):
    message: str


class GetFoodMenuResponse(BaseModel):
    food_id: int
    food_name: str
    description: str | None
    category: str
    price: float


# Create Cart to store Order Food
class AddToCart(BaseModel):
    food_id: int
    quantity: int


class CartItemResponse(BaseModel):
    food_id: int
    food_name: str
    quantity: int
    price: float
    total_price: float  # This field is already in your Cart model


# Model for the complete Cart Response including the total price
class CartResponse(BaseModel):
    cart_items: List[CartItemResponse]
    total_price: float  # Single total price for all cart items