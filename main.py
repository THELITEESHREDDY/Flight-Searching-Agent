from fastapi import FastAPI
from utils.db import base,engine
from user.routes import user_router
from agent.routes import agent_router
base.metadata.create_all(engine)



app = FastAPI()

app.include_router(agent_router)
app.include_router(user_router)

@app.get("/")
def hello():
    return {"welcome to backend"}