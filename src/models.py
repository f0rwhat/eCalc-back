from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()


class UtilInfo(Base):
    __tablename__ = "util_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    info = Column(String)


class Manager(Base):
    __tablename__ = "managers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    secondPhone = Column(String, nullable=True)
    identifier = Column(String)


class ElevatorType(Base):
    __tablename__= "elevator_type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    priceMultiplier = Column(Float)


class DeliveryType(Base):
    __tablename__ = "delivery_type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)


class PackageType(Base):
    __tablename__= "package_type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)


class GlassType(Base):
    __tablename__ = "glass_type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    discount = Column(Float)
    markup = Column(Float)

    price = relationship("GlassManufacturePrice", back_populates="glass", cascade='all,delete')


class GlassManufacture(Base):
    __tablename__ = "glass_manufacture"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    price = relationship("GlassManufacturePrice", back_populates="manufacture", cascade='all,delete')


class GlassManufacturePrice(Base):
    __tablename__ = "glass_manufacture_price"

    id = Column(Integer, primary_key=True, index=True)
    glass_id = Column(Integer, ForeignKey('glass_type.id'))
    manufacture_id = Column(Integer, ForeignKey('glass_manufacture.id'))
    price = Column(Float)

    glass = relationship("GlassType", back_populates="price")
    manufacture = relationship("GlassManufacture", back_populates="price")


class GlassDrawing(Base):
    __tablename__ = "glass_drawing"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    discount = Column(Float)
    markup = Column(Float)


class ProductType(Base):
    __tablename__ = "product_type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    products = relationship("Product", back_populates="type")
    components = relationship("Component", back_populates="type")


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    type_id = Column(Integer, ForeignKey('product_type.id'))
    name = Column(String)

    type = relationship("ProductType", back_populates="products")
    components = relationship("ProductComposition", back_populates="product")


class Component(Base):
    __tablename__ = "component"

    id = Column(Integer, primary_key=True, index=True)
    type_id = Column(Integer, ForeignKey('product_type.id'))
    name = Column(String)

    type = relationship("ProductType", back_populates="components")
    compositions = relationship("ProductComposition", back_populates="component")


class ProductComposition(Base):
    __tablename__ = "product_composition"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    component_id = Column(Integer, ForeignKey('component.id'))

    product = relationship("Product", back_populates="components")
    component = relationship("Component", back_populates="compositions")
