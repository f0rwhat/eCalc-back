from pydantic import BaseModel


class ResponseInfo(BaseModel):
    msg: str

    class Config:
        orm_mode = True
