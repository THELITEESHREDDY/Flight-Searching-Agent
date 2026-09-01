from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session

from . import controller 
from .schemas import ModelResponse
from user.models import UserTable
from utils.auth import get_current_user
from utils.db import get_db

agent_router = APIRouter(prefix="/chat",tags=["chat"])




@agent_router.get("/new_chat")
async def new_chat(db:Session=Depends(get_db),user:UserTable=Depends(get_current_user))->str:
    
    return  await controller.new_chat(str(user.id),db)





@agent_router.put("/{chat_id}/message")
async def generate_chat(message:str,chat_id:str,db:Session=Depends(get_db),user:UserTable=Depends(get_current_user))->list[ModelResponse]:
    return controller.generate_chat(str(user.id),message,chat_id,db)





@agent_router.get("/{chat_id}")
async def get_chat(chat_id,db:Session=Depends(get_db),user:UserTable=Depends(get_current_user))->list[ModelResponse]:
    return  await controller.get_chat(str(user.id),chat_id,db)




@agent_router.delete("/{chat_id}")
async def delete_chat(chat_id:str,user_id:str,db:Session=Depends(get_db),user:UserTable=Depends(get_current_user))->None:
    return await controller.delete_chat(str(user.id),chat_id,db)