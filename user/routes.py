from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session

from .schemas import user_response,create_user,TokenResponse
from user import controllers
from utils.db import get_db



user_router = APIRouter(prefix="/user")

@user_router.post("/register",response_model=user_response)
async def register_user(user:create_user,db:Session = Depends(get_db))->user_response:
    return await controllers.register_user(user,db)



@user_router.post("/login",response_model=TokenResponse)
async def login_user(user:create_user,db:Session = Depends(get_db))->TokenResponse:
    return await controllers.login_user(user,db)



