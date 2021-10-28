from pydantic import BaseModel


class UtilInfo(BaseModel):
    name: str
    info: str

    class Config:
        orm_mode = True


class ElevatorType(BaseModel):
    name: str
    priceMultiplier: float

    class Config:
        orm_mode = True


class ElevatorTypeOut(BaseModel):
    id: int


class DeliveryType(BaseModel):
    name: str
    price: float

    class Config:
        orm_mode = True


class PackageType(BaseModel):
    name: str
    price: float

    class Config:
        orm_mode = True


class ProductType(BaseModel):
    name: str

    class Config:
        orm_mode = True


class Product(BaseModel):
    name: str

    class Config:
        orm_mode = True


class Component(BaseModel):
    name: str

    class Config:
        orm_mode = True


class ProductComposition(BaseModel):
    product_id: int
    component_id: int

    class Config:
        orm_mode = True
