from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import or_, text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from app.database.db import get_session
from app.database.models import Category, Car, Client, Rental
from app.schemas import *
from pydantic import ValidationError

router = APIRouter()

def register(path, model, create_schema, patch_schema, search_fields):
    def fetch(session, item_id):
        obj = session.get(model, item_id)
        if obj is None:
            raise HTTPException(404, "Запись не найдена")
        return obj

    def validate(session, data, item_id=None):
        try:
            validated = create_schema.model_validate(data).model_dump()
        except ValidationError as exc:
            raise HTTPException(422, str(exc))
        refs = {Car: [("category_id", Category)], Rental: [("car_id", Car), ("client_id", Client)]}
        for field, target in refs.get(model, []):
            if session.get(target, validated[field]) is None:
                raise HTTPException(422, f"Не найдена связанная запись: {field}")
        if model is Rental:
            query = select(Rental).where(Rental.car_id == validated["car_id"],
                Rental.start_date < validated["end_date"], Rental.end_date > validated["start_date"])
            if item_id is not None:
                query = query.where(Rental.id != item_id)
            if session.exec(query).first():
                raise HTTPException(409, "Автомобиль уже арендован на эти даты")
        return validated

    def commit(session):
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(409, "Дубликат или запись используется в другой таблице")

    def listing(search: str = "", min_price: int | None = Query(None, ge=0),
                max_price: int | None = Query(None, ge=0), session: Session = Depends(get_session)):
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(422, "Минимальная цена больше максимальной")
        q = select(model)
        if search and search_fields:
            q = q.where(or_(*(getattr(model, f).contains(search, autoescape=True) for f in search_fields)))
        price = getattr(model, "daily_rate", None)
        if model is Car:
            q = q.join(Category)
            price = Category.daily_rate
        if price is not None:
            if min_price is not None: q = q.where(price >= min_price)
            if max_price is not None: q = q.where(price <= max_price)
        return session.exec(q.order_by(model.id)).all()

    def get_one(item_id: int, session: Session = Depends(get_session)):
        return fetch(session, item_id)

    def create(payload: create_schema, session: Session = Depends(get_session)):
        # SQLite reserves the writer before overlap checks, preventing concurrent double bookings.
        session.execute(text("BEGIN IMMEDIATE"))
        obj = model(**validate(session, payload.model_dump()))
        session.add(obj); commit(session); session.refresh(obj)
        return obj

    def patch(item_id: int, payload: patch_schema, session: Session = Depends(get_session)):
        session.execute(text("BEGIN IMMEDIATE"))
        obj = fetch(session, item_id)
        data = obj.model_dump()
        data.pop("id")
        data.update(payload.model_dump(exclude_unset=True))
        for key, value in validate(session, data, item_id).items():
            setattr(obj, key, value)
        session.add(obj); commit(session); session.refresh(obj)
        return obj

    def delete(item_id: int, session: Session = Depends(get_session)):
        obj = fetch(session, item_id)
        references = {Category: (Car.category_id,), Car: (Rental.car_id,), Client: (Rental.client_id,)}
        for column in references.get(model, ()):
            if session.exec(select(column).where(column == item_id)).first() is not None:
                raise HTTPException(409, "Сначала удалите связанные записи")
        session.delete(obj); commit(session)
        return Response(status_code=204)

    for suffix, endpoint, methods, response, status in [
        ("", listing, ["GET"], list[model], 200),
        ("/{item_id}", get_one, ["GET"], model, 200),
        ("", create, ["POST"], model, 201),
        ("/{item_id}", patch, ["PATCH"], model, 200),
        ("/{item_id}", delete, ["DELETE"], None, 204)]:
        router.add_api_route(path + suffix, endpoint, methods=methods,
            response_model=response, status_code=status, tags=[path[1:]], name=methods[0]+path)

register("/categories", Category, CategoryCreate, CategoryPatch, ["name"])
register("/cars", Car, CarCreate, CarPatch, ["brand", "model", "plate"])
register("/clients", Client, ClientCreate, ClientPatch, ["full_name", "license_number"])
register("/rentals", Rental, RentalCreate, RentalPatch, [])
