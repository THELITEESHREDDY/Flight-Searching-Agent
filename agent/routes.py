from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session

from . import controller 
from utils.db import get_db

agent_router = APIRouter(prefix="/chat",tags=["chat"])




@agent_router.get("/new_chat")
async def new_chat(db:Session=Depends(get_db))->str:
    
    return  await controller.new_chat(db)





@agent_router.put("/{id}/message")
async def generate_chat(userid:str,message:str,chatid:str,db:Session=Depends(get_db))->list[str]:
    return await controller.generate_chat(userid,message,chatid,db)





@agent_router.get("/{id}")
async def get_chat(id:str,db:Session=Depends(get_db))->list[str]:
    return  await controller.get_chat(id,db)




@agent_router.delete("/{id}")
async def delete_chat(id:str,db:Session=Depends(get_db))->None:
    return await controller.delete_chat(id,db)