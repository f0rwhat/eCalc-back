from pydantic import BaseModel, validator


class GlassType(BaseModel):
    name: str
    discount: float
    markup: float

    class Config:
        orm_mode = True

    @validator('name')
    def name_validator(cls, v):
        if v is None or v == '':
            raise ValueError("Не указано название типа!")
        return v

    @validator('discount', 'markup')
    def discount_and_markup_validator(cls, v):
        if v is None or v == '':
            raise ValueError("Не указана скидка или наценка!")
        try:
            temp = float(v)
        except Exception as e:
            raise ValueError("Скидка или наценка указаны некорректно!")
        return v


class GlassTypeOut(GlassType):
    id: int


class GlassManufacture(BaseModel):
    name: str

    class Config:
        orm_mode = True

    @validator('name')
    def name_validator(cls, v):
        if v is None or v == '':
            raise ValueError("Не указано название обработки!")
        return v


class GlassManufactureOut(GlassManufacture):
    id: int


class GlassManufacturePrice(BaseModel):
    price: float

    class Config:
        orm_mode = True

    @validator('price')
    def price_validator(cls, v):
        if v is None or v == '':
            raise ValueError("Не указана цена за обработку!")
        try:
            temp = float(v)
        except Exception as e:
            raise ValueError("Цена указана некорректно!")
        return v


class GlassManufacturePriceOut(GlassManufacturePrice):
    price: float
    glass_id: int
    manufacture_id: int

    class Config:
        orm_mode = True


class GlassDrawing(BaseModel):
    name: str
    price: float
    discount: float
    markup: float

    class Config:
        orm_mode = True