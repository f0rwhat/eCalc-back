from typing import Union, List
from starlette import status
from fastapi import APIRouter, Response
from fastapi_sqlalchemy import db
from src.schemas.manager import Manager, ManagerOut
from src.schemas.info import ResponseInfo
from src.models import Manager as ManagerModel


router = APIRouter()


@router.get("/manager/all", response_model=List[ManagerOut])
def get_all_managers():
    return db.session.query(ManagerModel).all()


@router.post("/manager/add", response_model=List[ManagerOut])
def create_manager(manager: Manager):
    db_manager = ManagerModel(
        name=manager.name, phone=manager.phone, secondPhone=manager.secondPhone, identifier=manager.identifier
    )
    db.session.add(db_manager)
    db.session.commit()
    return get_all_managers()


@router.delete("/manager/{manager_id}", response_model=Union[List[ManagerOut], ResponseInfo])
def delete_manager(manager_id: int, response: Response):
    db_manager = get_manager_by_id(manager_id)
    if db_manager is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseInfo(msg="Указанного менеджера нет в базе данных")
    db.session.delete(db_manager)
    db.session.commit()
    return get_all_managers()


@router.put("/manager/{manager_id}", response_model=Union[List[ManagerOut], ResponseInfo])
def update_manager(manager_id: int, manager: Manager, response: Response):
    db_manager = get_manager_by_id(manager_id)

    if db_manager is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseInfo(msg="Указанного менеджера нет в базе данных")

    db_manager.name = manager.name
    db_manager.phone = manager.phone
    db_manager.secondPhone = manager.secondPhone
    db_manager.identifier = manager.identifier
    db.session.commit()
    return get_all_managers()


def get_manager_by_id(manager_id: int) -> Manager:
    return db.session.query(ManagerModel).filter(ManagerModel.id == manager_id).first()
