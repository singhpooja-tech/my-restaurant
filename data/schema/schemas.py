from pydantic import BaseModel, EmailStr, constr, field_validator
from typing import Optional
from datetime import datetime


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


class FoodCategoryCreate(BaseModel):
    name: str
    image_url: Optional[bytes] = None  # Binary image data
    is_active: bool = True

