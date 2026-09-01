import uuid
from fastapi import HTTPException,status
from datetime import datetime,timezone
from sqlalchemy import String, Text, DateTime,desc
from sqlalchemy.orm import Session

from .models import ChatSessionTable, MessageTable
from .schemas import ModelResponse,ChatRole
from .agent import Agent,client,SYSTEM_PROMPT,tools


async def new_chat(userid: str, db: Session)->str:

    try:
        new_session = ChatSessionTable(
            id=str(uuid.uuid4()),
            user_id=userid,
            created_at=datetime.now(timezone.utc)
        )
        

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        return new_session.id

    except (KeyError, ValueError) as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {e}"
        )



def generate_chat(
    user_id: str,
    message: str,
    chat_id: str,
    db: Session
)->list[ModelResponse]:
    
    chat_session = (
        db.query(ChatSessionTable)
        .filter(ChatSessionTable.id == chat_id)
        .first()
    )

    
    if chat_session is None or chat_session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to do this"
        )

    
    chat_history = (
        db.query(MessageTable)
        .filter(MessageTable.session_id == chat_id)
        .order_by(MessageTable.timestamp.desc())
        .all()
    )

    chat_history_schema = [
        {
            "role": msg.role.value,
            "content": msg.content
        }
        for msg in chat_history
    ]

    agent = Agent(
        client,
        SYSTEM_PROMPT,
        tools,
        chat_history_schema
    )

    
    user_message = MessageTable(
        id=str(uuid.uuid4()),
        session_id=chat_id,
        role=ChatRole.user.value,
        content=message,
        timestamp=datetime.now(timezone.utc)
    )

    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    
    response = agent(message)

    
    agent_message = MessageTable(
        id=str(uuid.uuid4()),
        session_id=chat_id,
        role=ChatRole.assistant.value,
        content=response,
        timestamp=datetime.now(timezone.utc)
    )

    db.add(agent_message)
    db.commit()
    db.refresh(agent_message)

    
    messages = (
        db.query(MessageTable)
        .filter(MessageTable.session_id == chat_id)
        .order_by(MessageTable.timestamp.asc())
        .all()
    )

    return messages
    


    

async def get_chat(user_id:str,chat_id:str,db:Session)->list[ModelResponse]:
    chat_session = (
        db.query(ChatSessionTable)
        .filter(ChatSessionTable.id == chat_id)
        .first()
    )

    if chat_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="chat id not found"
        )
        
    if chat_session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to do this"
        )
    
        
    chat_history = (
        db.query(MessageTable)
        .filter(MessageTable.session_id == chat_id)
        .order_by(MessageTable.timestamp.desc())
        .all()
    )

    chat_history_schema = [
        ModelResponse(
            id=msg.id,
            role=msg.role.value,
            content=msg.content
        )
        for msg in chat_history
    ]

    return chat_history_schema



async def delete_chat(
    user_id: str,
    chat_id: str,
    db: Session
):
    try:

        
        chat_session = (
            db.query(ChatSessionTable)
            .filter(
                ChatSessionTable.id == chat_id,
                ChatSessionTable.user_id == user_id
            )
            .first()
        )

        
        if chat_session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )

        
        db.query(MessageTable).filter(
            MessageTable.session_id == chat_id
        ).delete(
            synchronize_session=False
        )

        
        db.delete(chat_session)

        
        db.commit()

        return 

    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Uncaught error"
        )

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting chat: {e}"
        )