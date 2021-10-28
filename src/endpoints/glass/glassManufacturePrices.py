from typing import Union, List
from starlette import status
import json
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Response, WebSocket
from fastapi_sqlalchemy import db
from src.schemas.glass import GlassType, GlassManufacturePrice, \
    GlassManufacturePriceOut
from src.schemas.info import ResponseInfo
from src.models import GlassManufacturePrice as GlassManufacturePriceModel


router = APIRouter()


@router.get("/glass/price/all", response_model=Union[List[GlassManufacturePriceOut], ResponseInfo])
def get_all_glass_prices():
    return db.session.query(GlassManufacturePriceModel).all()


@router.get("/glass/price/{glass_type_id}/{glass_manufacture_id}",
            response_model=Union[GlassManufacturePrice, ResponseInfo])
def get_glass_price(glass_type_id: int, glass_manufacture_id: int):
    return get_glass_price(glass_type_id, glass_manufacture_id)


@router.post("/glass/price/{glass_type_id}/{glass_manufacture_id}", response_model=List[GlassManufacturePriceOut])
def add_glass_price(glass_type_id: int,
                    glass_manufacture_id: int,
                    glass_manufacture_price: GlassManufacturePrice):
    glass_manufacture_price = GlassManufacturePriceModel(
        glass_id=glass_type_id, manufacture_id=glass_manufacture_id, price=glass_manufacture_price.price
    )
    db.session.add(glass_manufacture_price)
    db.session.commit()
    return get_all_glass_prices()


@router.delete("/glass/price/{glass_type_id}/{glass_manufacture_id}",
               response_model=Union[List[GlassManufacturePriceOut], ResponseInfo])
def delete_glass_price(glass_type_id: int,
                       glass_manufacture_id: int,
                       response: Response):
    db_glass_manufacture_price = get_glass_price(glass_type_id, glass_manufacture_id)
    if db_glass_manufacture_price is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseInfo(msg="Цены за стекло в указанной обработке нет в базе данных!")
    db.session.delete(db_glass_manufacture_price)
    db.session.commit()
    return get_all_glass_prices()


@router.put("/glass/price/{glass_type_id}/{glass_manufacture_id}",
            response_model=Union[List[GlassManufacturePriceOut], ResponseInfo])
def update_glass_price(glass_type_id: int,
                       glass_manufacture_id: int,
                       glass_manufacture_price: GlassManufacturePrice,
                       response: Response):
    db_glass_manufacture_price = get_glass_price(glass_type_id, glass_manufacture_id)
    if db_glass_manufacture_price is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ResponseInfo(msg="Цена за стекло в указанной обработке не указана")
    db_glass_manufacture_price.price = glass_manufacture_price.price
    db.session.commit()
    return get_all_glass_prices()


def get_glass_price(glass_type_id: int, glass_manufacture_id: int) -> GlassType:
    return db.session.query(GlassManufacturePriceModel).filter(
        GlassManufacturePriceModel.glass_id == glass_type_id,
        GlassManufacturePriceModel.manufacture_id == glass_manufacture_id
    ).first()


class ManufacturePricesWebsocketManager:
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

    async def add_price(self, data: dict, websocket: WebSocket):
        try:
            GlassManufacturePrice.price_validator(data["price"])
        except Exception as e:
            notification = {'message_type': 'notification', 'data': {'notification_type': 'error',
                                                                     'header': 'Ошибка!',
                                                                     'message': str(e)}}
            notification_json = jsonable_encoder(notification)
            await self.send_personal_message(notification_json, websocket)
            return

        db_glass_price = GlassManufacturePriceModel(
            glass_id=data['glass_type_id'], manufacture_id=data['glass_manufacture_id'], price=data['price']
        )
        with db():
            db.session.add(db_glass_price)
            db.session.commit()
            response = {'message_type': 'get', 'data': get_all_glass_prices()}
            response_json = jsonable_encoder(response)
            await self.broadcast(response_json)
            notification = {'message_type': 'notification', 'data': {'notification_type': 'success',
                                                                     'header': 'Цена успешно добавлена!',
                                                                     'message': 'Ура!'}}
            notification_json = jsonable_encoder(notification)
            await self.send_personal_message(notification_json, websocket)

    async def update_price(self, data: dict, websocket: WebSocket):
        try:
            GlassManufacturePrice.price_validator(data["price"])
        except Exception as e:
            notification = {'message_type': 'notification', 'data': {'notification_type': 'error',
                                                                     'header': 'Ошибка!',
                                                                     'message': str(e)}}
            notification_json = jsonable_encoder(notification)
            await self.send_personal_message(notification_json, websocket)
            return
        with db():
            db_glass_price = get_glass_price(int(data['glass_type_id']), int(data['glass_manufacture_id']))
            if db_glass_price is not None:
                db_glass_price.price = data['price']
                db.session.commit()
                response = {'message_type': 'get', 'data': get_all_glass_prices()}
                response_json = jsonable_encoder(response)
                await self.broadcast(response_json)
                notification = {'message_type': 'notification', 'data': {'notification_type': 'success',
                                                                         'header': 'Цена успешно обновлена!',
                                                                         'message': 'Ура!'}}
                notification_json = jsonable_encoder(notification)
                await self.send_personal_message(notification_json, websocket)
            else:
                notification = {'message_type': 'notification', 'data': {'notification_type': 'error',
                                                                         'header': 'Не удалось обновить цену!',
                                                                         'message': 'Цены за стекло в указанной обработке нет в базе данных!'}}
                notification_json = jsonable_encoder(notification)
                await self.send_personal_message(notification_json, websocket)

    async def delete_price(self, data: dict, websocket: WebSocket):
        with db():
            db_glass_price = get_glass_price(int(data['glass_type_id']), int(data['glass_manufacture_id']))
            if db_glass_price is not None:
                db.session.delete(db_glass_price)
                db.session.commit()
                response = {'message_type': 'get', 'data': get_all_glass_prices()}
                response_json = jsonable_encoder(response)
                await self.broadcast(response_json)
                notification = {'message_type': 'notification', 'data': {'notification_type': 'success',
                                                                         'header': 'Цена успешно удалена!',
                                                                         'message': 'Ура!'}}
                notification_json = jsonable_encoder(notification)
                await self.send_personal_message(notification_json, websocket)
            else:
                notification = {'message_type': 'notification', 'data': {'notification_type': 'error',
                                                                         'header': 'Не удалось обновить цену!',
                                                                         'message': 'Цены за стекло в указанной обработке нет в базе данных!'}}
                notification_json = jsonable_encoder(notification)
                await self.send_personal_message(notification_json, websocket)

    async def get_prices(self, websocket: WebSocket):
        response = {'message_type': 'get', 'data': get_all_glass_prices()}
        response_json = jsonable_encoder(response)
        await self.send_personal_message(response_json, websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str, broadcast_except: WebSocket = None):
        for connection in self.active_connections:
            # if broadcast_except is None or broadcast_except == connection:
            await connection.send_json(message)


websocket_manager = ManufacturePricesWebsocketManager()


@router.websocket("/ws/glass/price")
async def types_websocket(websocket: WebSocket):
    print('Accepting client connection...')
    await websocket_manager.connect(websocket)
    while True:
        try:
            # Wait for any message from the client
            request_json = await websocket.receive_text()
            request = json.loads(request_json)
            print(request)
            if request['message_type'] == 'add':
                await websocket_manager.add_price(request['data'], websocket)

            if request['message_type'] == 'update':
                await websocket_manager.update_price(request['data'], websocket)

            if request['message_type'] == 'delete':
                await websocket_manager.delete_price(request['data'], websocket)

            if request['message_type'] == 'get':
                await websocket_manager.get_prices(websocket)

        except Exception as e:
            websocket_manager.disconnect(websocket)
            break
