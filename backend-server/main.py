from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from databases import UserBase
import logging

class EndpointFilter(logging.Filter):
    def __init__(self, path: str):
        super().__init__()
        self._path = path

    def filter(self, record: logging.LogRecord) -> bool:
        return record.args and len(record.args) >= 3 and record.args[2] != self._path and record.args[4] != 200
    
base = UserBase("users.db")
app = FastAPI()
codes = {}

uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.addFilter(EndpointFilter("/codes"))

class CodeObject(BaseModel):
    user: str
    code: int

class RegisterObject(BaseModel):
    userid: str
    nickname: str

@app.get("/check")
async def check_player(nickname: str, ip: str = "52.52.52.52"):
    result = await base.check_user(nickname, ip)

    if result: return {"answer": 'pass'}
    else:
        result = await base.get_user(nickname)
        if result: return {"answer": 'need login'}
        else: return {"answer": 'not exists'}

@app.get("/quit")
async def mark_quit(nickname: str, ip: str):
    await base.update_user(nickname, ip)

@app.get("/reset")
async def reset_table():
    await base.reset_table()

@app.get("/codes")
async def get_codes():
    buffer = codes.copy()
    codes.clear()
    return buffer

@app.post("/send")
async def send_code(data: CodeObject):
    user = await base.get_user(data.user)
    codes[user[3]] = data.code

@app.post("/register")
async def register_user(data: RegisterObject):
    findnickname = await base.get_user(data.nickname.lower())
    finduserid = await base.get_user_by_id(data.userid)

    if findnickname:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nickname already exists"
        )
    
    if finduserid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="UserID already exists"
        )
    
    await base.add_user(data.nickname.lower(), data.userid)