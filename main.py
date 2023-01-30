from fastapi import FastAPI
from schemas import User

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/users")
async def create_user(user: User):
    #cria o usuario
    return {"message": "user created"}

@app.get("/users")
async def get_users():
    #retorna lista de usuarios
    return {"message":"list of usuers"}

@app.get("/users/{user_id}")
async def read_user(user_id:str):
    #retorna um usuario
    return {"message":"get a user"}

@app.put("/users/{user_id}")
async def read_user(user_id:str, user:User):
    #update usuario
    return {"message":"updated user"}


