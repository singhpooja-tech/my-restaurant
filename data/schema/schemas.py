from pydantic import BaseModel, EmailStr, constr, field_validator
from typing import Optional


# User Signup Schema
class UserCreate(BaseModel):
    user_name: str
    email: EmailStr
    password: constr(min_length=6)  # Password must be at least 6 characters long
    fullname: Optional[str] = None
    address: Optional[str] = None
    phone_no: Optional[str] = None  # Changed to string for flexibility
    post_code: Optional[int] = None

    @field_validator("phone_no")
    def validate_phone(cls, v):
        if v and len(v) < 10:
            raise ValueError("Phone number must be at least 10 characters long.")
        elif v and len(v) > 10:
            raise ValueError("Phone number must be 10 characters long.")
        return v

    @field_validator("post_code")
    def validate_post_code(cls, v):
        if v and len(str(v)) < 5:
            raise ValueError("Post code must be at least 5 digits long.")
        return v


# JWT Token Response Schema
class TokenResponse(BaseModel):
    access_token: str
    token_type: str