import uuid
from fastapi import HTTPException,status,Query

from .models import UserTable
from .schemas import create_user,user_response,TokenResponse
from utils.auth import verify_password, create_access_token,hash_password
from sqlalchemy.orm import Session


async def register_user(user:create_user,db:Session)->user_response:

    new_user_data = user.model_dump()

    if((new_user_data.get("email")is None) or (new_user_data.get("password") is None)):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="provide all the required details"
            ) 

    existing_user = db.query(UserTable).where(UserTable.email==new_user_data.get("email")).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user exists"
        )

    new_user = UserTable(
            id=str(uuid.uuid4()),
            email=new_user_data["email"],
            hashed_password=hash_password(new_user_data["password"])
        )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    
    return new_user




async def login_user(user:create_user,db:Session)->TokenResponse:

    user_data = user.model_dump()

    if((user_data.get("email") is None) or (user_data.get("password") is None)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="provide required details"
        )

    existing_user = db.query(UserTable).where(UserTable.email==user_data.get("email")).first()
    
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user does not exist"
        )

    if not verify_password(user.password, existing_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        user_id=str(existing_user.id)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
