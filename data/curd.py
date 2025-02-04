from sqlalchemy.orm import session
from data.schema.schemas import UserCreate
from data.model.models import User
from passlib.context import CryptContext

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def create_user(db: session, user: UserCreate):
    hashed_password = hash_password(user.password)  # Hashing password
    db_user = User(
        user_name=user.user_name,
        email=user.email,
        password=hashed_password,
        fullname=user.fullname,
        address=user.address,
        phone_no=user.phone_no,
        post_code=user.post_code
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
