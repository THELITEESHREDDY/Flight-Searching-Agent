import uuid
from fastapi import HTTPException,status,Query
from datetime import datetime,timezone
from sqlalchemy import String, Text, DateTime,desc
from sqlalchemy.orm import Session

from .models import ChatRole, ChatSessionTable, MessageTable
from .agent import Agent,client,SYSTEM_PROMPT,tools


async def new_chat(userid:str,db:Session):

    try:

        new_session = ChatSessionTable(
            id=str(uuid.uuid4()),
            user_id=userid,
            created_at = DateTime(datetime.now()) 
        )

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        return new_session.id

    except (KeyError,ValueError) as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {e}"
        )



async def generate_chat(user_id:str,message:str,chat_id:str,db:Session):
    chat_user_id = db.query(ChatSessionTable).where(user_id==user_id).first()

    if chat_user_id is None or chat_user_id!=user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to do this"
        )

    chat_history = db.query(MessageTable).where(MessageTable.session_id==chat_id).order_by(desc(MessageTable.timestamp)).limit(20).all()

    agent = Agent(client,SYSTEM_PROMPT,tools,chat_history)

    user_message = MessageTable(
        id=chat_id,
        session_id=chat_id,
        role="user",
        content=message,
        timestamp = DateTime(datetime.now(timezone.utc()))
    )
    db.add(user_message)
    db.commit()
    
    response = agent(message)
    agent_message = MessageTable(
        id=
    )
    return
    


    

async def get_chat(id:str="")->list[str]:
    return ["get chat"]

async def delete_chat(id:str):
    print("delete chat")