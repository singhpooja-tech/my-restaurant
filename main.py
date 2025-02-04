from fastapi import FastAPI, Depends, HTTPException
from data.database import *
from data.curd import *

app = FastAPI()
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/user/create")
def create_user_api(user: UserCreate, db: session = Depends(get_db)):
    # Validate if all required fields are present, if not raise an error
    if not user.user_name or not user.password or not user.fullname:
        raise HTTPException(status_code=400, detail="Missing required fields")
    return create_user(db,user)
