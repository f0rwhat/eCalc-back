from pydantic import BaseModel, Field, validator
from typing import Optional
import re


class Manager(BaseModel):
    name: str
    phone: str
    secondPhone: Optional[str] = Field(None)
    identifier: str

    class Config:
        orm_mode = True

    @validator('phone', 'secondPhone')
    def phone_validator(cls, v):
        if v is not None and not re.match(r'\+?\b[\d]\([\d]{3}\)[\d]{3}-[\d]{2}-[\d]{2}\b', v):
            raise ValueError("Некорректный телефон")
        return v

    @validator('name', 'identifier', 'phone')
    def required_field_validator(cls, v):
        if v is None or v == '':
            raise ValueError("Заполнены не все обязательные поля (имя, телефон или идентификатор)")
        return v


class ManagerOut(Manager):
    id: int
