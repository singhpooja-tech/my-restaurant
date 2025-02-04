from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    user_name: str
    email: EmailStr
    password: constr(min_length=6)  # Added password validation
    fullname: str = None
    address: str = None
    phone_no: str = None  # Changed to string
    post_code: int = None
