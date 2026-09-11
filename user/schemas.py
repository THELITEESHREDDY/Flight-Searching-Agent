from pydantic import BaseModel,EmailStr


class create_user(BaseModel):
    email:EmailStr
    password:str

class user_response(BaseModel):
    email:EmailStr
    id:str

class TokenResponse(BaseModel):
    access_token:str    
    token_type:str