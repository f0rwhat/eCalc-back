from typing import Union, List
from starlette import status
import json
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Response, WebSocket
from fastapi_sqlalchemy import db
from src.schemas.glass import GlassType, GlassManufacture, GlassManufactureOut
from src.schemas.info import ResponseInfo
from src.models import GlassManufacture as GlassManufactureModel


router = APIRouter()


@router.get("/glass/manufacture/all", response_model=List[GlassManufactureOut])
def get_all_glass_manufactures():
    return db.session.query(GlassManufactureModel).all()


@router.post("/glass/manufacture/add", response_model=List[GlassManufactureOut])
def add_glass_manufacture(glass_manufacture: GlassManufacture):
    db_glass_manufacture = GlassManufactureModel(name=glass_manufacture.name)
    db.session.add(db_glass_manufacture)
    db.session.commit()
    return get_all_glass_manufactures()


@router.delete("/glass/manufacture/{glass_manufacture_id}",
               response_model=Union[List[GlassManufactureOut], ResponseInfo])
def delete_glass_manufacture(glass_manufacture_id: int, response: Response):
    db_glass_manufacture = get_glass_manufacture_by_id(glass_manufacture_id)
    if db_glass_manufacture is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseInfo(msg="Указанной обработки стекла не существует")
    db.session.delete(db_glass_manufacture)
    db.session.commit()
    return get_all_glass_manufactures()


@router.put("/glass/manufacture/{glass_manufacture_id}", response_model=Union[List[GlassManufactureOut], ResponseInfo])
def update_glass_manufacture(glass_manufacture_id: int, glass_manufacture: GlassManufacture, response: Response):
    db_glass_manufacture = get_glass_manufacture_by_id(glass_manufacture_id)
    if db_glass_manufacture is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseInfo(msg="Указанной обработки стекла не существует")
    db_glass_manufacture.name = glass_manufacture.name
    db.session.commit()
    return get_all_glass_manufactures()


def get_glass_manufacture_by_id(glass_manufacture_id: int) -> GlassType:
    return db.session.query(GlassManufactureModel).filter(GlassManufactureModel.id == glass_manufacture_id).first()


class ManufacturesWebsocketManager:
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

    async def add_manufacture(self, data: dict, websocket: WebSocket):
        try:
            GlassManufacture.name_validator(data["name"])
        except Exception as e:
            notification = {'message_type': 'notification', 'data': {'notification_type': 'error',
                                                                     'header': 'Ошибка!',
                                                                     'message': str(e)}}
            notification_json = jsonable_encoder(notification)
            await self.send_personal_message(notification_json, websocket)
            return

        db_glass_manufacture = GlassManufactureModel(
            name=data['name']
        )
        with db():
            db.session.add(db_glass_manufacture)
            db.session.commit()
            response = {'message_type': 'get', 'data': get_all_glass_manufactures()}
            response_json = jsonable_encoder(response)
            await self.broadcast(response_json)
            notification = {'message_type': 'notification', 'data': {'notification_type': 'success',
                                                                     'header': 'Новая обработка стекла успешно добавлена!',
                                                                     'message': 'Ура!'}}
            notification_json = jsonable_encoder(notification)
            await self.send_personal_message(notification_json, websocket)

    async def update_manufacture(self, data: dict, websocket: WebSocket):
        try:
            GlassManufacture.name_validator(data["name"])
        except Exception as e:
            notification = {'message_type': 'notification', 'data': {'notification_type': 'error',
                                                                     'header': 'Ошибка!',
                                                                     'message': str(e)}}
            notification_json = jsonable_encoder(notification)
            await self.send_personal_message(notification_json, websocket)
            return

        with db():
            db_glass_type = get_glass_manufacture_by_id(int(data['id']))
            if db_glass_type is not None:
                db_glass_type.name = data['name']
                db.session.commit()
                response = {'message_type': 'get', 'data': get_all_glass_manufactures()}
                response_json = jsonable_encoder(response)
                await self.broadcast(response_json)
                notification = {'message_type': 'notification', 'data': {'notification_type': 'success',
                                                                         'header': 'Данные об обработке стекла успешно изменены!',
                                                                         'message': 'Ура!'}}
                notification_json = jsonable_encoder(notification)
                await self.send_personal_message(notification_json, websocket)
            else:
                notification = {'message_type': 'notification', 'data': {'notification_type': 'error',
                                                                         'header': 'Не удалось изменить данные об обработке стекла!',
                                                                         'message': 'Указанной обработки стекла нет в базе данных'}}
                notification_json = jsonable_encoder(notification)
                await self.send_personal_message(notification_json, websocket)

    async def delete_manufacture(self, data: dict, websocket: WebSocket):
        with db():
            db_glass_type = get_glass_manufacture_by_id(int(data['id']))
            if db_glass_type is not None:
                db.session.delete(db_glass_type)
                db.session.commit()
                response = {'message_type': 'get', 'data': get_all_glass_manufactures()}
                response_json = jsonable_encoder(response)
                await self.broadcast(response_json)
                notification = {'message_type': 'notification', 'data': {'notification_type': 'success',
                                                                         'header': 'Обработка стекла успешно удалена!',
                                                                         'message': 'Ура!'}}
                notification_json = jsonable_encoder(notification)
                await self.send_personal_message(notification_json, websocket)
            else:
                notification = {'message_type': 'notification', 'data': {'notification_type': 'error',
                                                                         'header': 'Не удалось удалить обработку стекла!',
                                                                         'message': 'Указанной обработки стекла нет в базе данных'}}
                notification_json = jsonable_encoder(notification)
                await self.send_personal_message(notification_json, websocket)

    async def get_manufactures(self, websocket: WebSocket):
        with db():
            response = {'message_type': 'get', 'data': get_all_glass_manufactures()}
            response_json = jsonable_encoder(response)
            await self.send_personal_message(response_json, websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str, broadcast_except: WebSocket = None):
        for connection in self.active_connections:
            #if broadcast_except is None or broadcast_except == connection:
            await connection.send_json(message)


websocket_manager = ManufacturesWebsocketManager()


@router.websocket("/ws/glass/manufacture")
async def manufactures_websocket(websocket: WebSocket):
    print('Accepting client connection...')
    await websocket_manager.connect(websocket)
    while True:
        try:
            # Wait for any message from the client
            request_json = await websocket.receive_text()
            request = json.loads(request_json)
            print(request)
            if request['message_type'] == 'add':
                await websocket_manager.add_manufacture(request['data'], websocket)

            if request['message_type'] == 'update':
                await websocket_manager.update_manufacture(request['data'], websocket)

            if request['message_type'] == 'delete':
                await websocket_manager.delete_manufacture(request['data'], websocket)

            if request['message_type'] == 'get':
                await websocket_manager.get_manufactures(websocket)

        except Exception as e:
            websocket_manager.disconnect(websocket)
            break

