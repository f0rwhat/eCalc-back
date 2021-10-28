from typing import Union, List

from pydantic import ValidationError
from starlette import status
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Response, WebSocket, WebSocketDisconnect
from fastapi_sqlalchemy import db
from src.schemas.glass import GlassType, GlassTypeOut
from src.schemas.info import ResponseInfo
from src.models import GlassType as GlassTypeModel
import json

router = APIRouter()


@router.get("/glass/type/all", response_model=List[GlassTypeOut])
def get_all_glass_types():
    return db.session.query(GlassTypeModel).all()


@router.post("/glass/type/add", response_model=List[GlassTypeOut])
def add_glass_type(glass_type: GlassType):
    db_glass_type = GlassTypeModel(
        name=glass_type.name, discount=glass_type.discount, markup=glass_type.markup
    )
    db.session.add(db_glass_type)
    db.session.commit()
    return get_all_glass_types()


@router.delete("/glass/type/{glass_type_id}", response_model=Union[List[GlassTypeOut], ResponseInfo])
def delete_glass_type(glass_type_id: int, response: Response):
    db_glass_type = get_glass_type_by_id(glass_type_id)
    if db_glass_type is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseInfo(msg="Указанного типа стекла нет в базе данных")
    db.session.delete(db_glass_type)
    db.session.commit()
    return get_all_glass_types()


@router.put("/glass/type/{glass_type_id}", response_model=Union[List[GlassTypeOut], ResponseInfo])
def update_glass_type(glass_type_id: int, glass_type: GlassType, response: Response):
    db_glass_type = get_glass_type_by_id(glass_type_id)
    if db_glass_type is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseInfo(msg="Указанного типа стекла нет в базе данных")
    db_glass_type.name = glass_type.name
    db_glass_type.discount = glass_type.discount
    db_glass_type.markup = glass_type.markup
    db.session.commit()
    return get_all_glass_types()


def get_glass_type_by_id(glass_type_id: int) -> GlassType:
    return db.session.query(GlassTypeModel).filter(GlassTypeModel.id == glass_type_id).first()


class TypesWebsocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        try:
            self.active_connections.remove(websocket)
        except Exception as e:
            pass

    async def add_type(self, data: dict, websocket: WebSocket):
        try:
            GlassType.name_validator(data["name"])
            GlassType.discount_and_markup_validator(data["discount"])
            GlassType.discount_and_markup_validator(data["markup"])
        except Exception as e:
            notification = {'message_type': 'notification', 'data': {'notification_type': 'error',
                                                                     'header': 'Ошибка!',
                                                                     'message': str(e)}}
            notification_json = jsonable_encoder(notification)
            await self.send_personal_message(notification_json, websocket)
            return

        db_glass_type = GlassTypeModel(
            name=data['name'], discount=data['discount'], markup=data['markup']
        )
        with db():
            db.session.add(db_glass_type)
            db.session.commit()
            response = {'message_type': 'get', 'data': get_all_glass_types()}
            response_json = jsonable_encoder(response)
            await self.broadcast(response_json)
            notification = {'message_type': 'notification', 'data': {'notification_type': 'success',
                                                                     'header': 'Новый тип стекла успешно создан!',
                                                                     'message': 'Ура!'}}
            notification_json = jsonable_encoder(notification)
            await self.send_personal_message(notification_json, websocket)

    async def update_type(self, data: dict, websocket: WebSocket):
        try:
            GlassType.name_validator(data["name"])
            GlassType.discount_and_markup_validator(data["discount"])
            GlassType.discount_and_markup_validator(data["markup"])
        except Exception as e:
            notification = {'message_type': 'notification', 'data': {'notification_type': 'error',
                                                                     'header': 'Ошибка!',
                                                                     'message': str(e)}}
            notification_json = jsonable_encoder(notification)
            await self.send_personal_message(notification_json, websocket)
            return

        with db():
            db_glass_type = get_glass_type_by_id(int(data['id']))
            if db_glass_type is not None:
                db_glass_type.name = data['name']
                db_glass_type.discount = data['discount']
                db_glass_type.markup = data['markup']
                db.session.commit()
                response = {'message_type': 'get', 'data': get_all_glass_types()}
                response_json = jsonable_encoder(response)
                await self.broadcast(response_json)
                notification = {'message_type': 'notification', 'data': {'notification_type': 'success',
                                                                         'header': 'Данные о типе стекла успешно обновлены!',
                                                                         'message': 'Ура!'}}
                notification_json = jsonable_encoder(notification)
                await self.send_personal_message(notification_json, websocket)
            else:
                notification = {'message_type': 'notification', 'data': {'notification_type': 'error',
                                                                         'header': 'Не удалось обновить данные о типе стекла!',
                                                                         'message': 'Указанного типа стекла нет в базе данных'}}
                notification_json = jsonable_encoder(notification)
                await self.send_personal_message(notification_json, websocket)

    async def delete_type(self, data: dict, websocket: WebSocket):
        with db():
            db_glass_type = get_glass_type_by_id(int(data['id']))
            if db_glass_type is not None:
                db.session.delete(db_glass_type)
                db.session.commit()
                response = {'message_type': 'get', 'data': get_all_glass_types()}
                response_json = jsonable_encoder(response)
                await self.broadcast(response_json)
                notification = {'message_type': 'notification', 'data': {'notification_type': 'success',
                                                                         'header': 'Тип стекла успешно удален!',
                                                                         'message': 'Ура!'}}
                notification_json = jsonable_encoder(notification)
                await self.send_personal_message(notification_json, websocket)
            else:
                notification = {'message_type': 'notification', 'data': {'notification_type': 'error',
                                                                         'header': 'Не удалось удалить тип стекла!',
                                                                         'message': 'Указанного типа стекла нет в базе данных'}}
                notification_json = jsonable_encoder(notification)
                await self.send_personal_message(notification_json, websocket)

    async def get_types(self, websocket: WebSocket):
        response = {'message_type': 'get', 'data': get_all_glass_types()}
        response_json = jsonable_encoder(response)
        await self.send_personal_message(response_json, websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str, broadcast_except: WebSocket = None):
        for connection in self.active_connections:
            # if broadcast_except is None or broadcast_except == connection:
            await connection.send_json(message)


websocket_manager = TypesWebsocketManager()


@router.websocket("/ws/glass/type")
async def manufacture_prices_websocket(websocket: WebSocket):
    print('Accepting client connection...')
    await websocket_manager.connect(websocket)
    while True:
        try:
            # Wait for any message from the client
            request_json = await websocket.receive_text()
            request = json.loads(request_json)
            print(request)
            if request['message_type'] == 'add':
                await websocket_manager.add_type(request['data'], websocket)

            if request['message_type'] == 'update':
                await websocket_manager.update_type(request['data'], websocket)

            if request['message_type'] == 'delete':
                await websocket_manager.delete_type(request['data'], websocket)

            if request['message_type'] == 'get':
                await websocket_manager.get_types(websocket)

        except Exception as e:
            websocket_manager.disconnect(websocket)
            break
