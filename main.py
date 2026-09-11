from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.db import base,engine
from user.routes import user_router
from agent.routes import agent_router
base.metadata.create_all(engine)

from utils.settings import settings

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router)
app.include_router(user_router)

@app.get("/")
def hello():
    return {"welcome to backend"}