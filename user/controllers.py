import uuid
from fastapi import HTTPException,status,Query

from .models import UserTable
from .schemas import create_user,user_response
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
            hashed_password=new_user_data["password"]
        )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    
    return new_user




async def login_user(user:create_user,db:Session)->user_response:

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

    if existing_user.hashed_password != user_data.get("password"):
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user does not exist"
            )
    
    return existing_user



async def logout_user():
    return {"email":"logoutuser@gmail.com"}