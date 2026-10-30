from sqlmodel import Session, select
from sqlalchemy import text
from app.database.db import engine
from app.database.models import Category, Car, Client, Rental

engine.echo = False
with Session(engine) as session:
    print("AutoRent — проверка действующей database.db")
    for model in (Category, Car, Client, Rental):
        rows = session.exec(select(model)).all()
        print(f"{model.__tablename__}: {len(rows)} записей")
    assert session.exec(text("PRAGMA foreign_keys")).scalar() == 1
    assert session.exec(text("PRAGMA foreign_key_check")).all() == []
    print("Внешние ключи включены; нарушений нет.")
    for rental in session.exec(select(Rental)).all():
        print(f"Аренда {rental.id}: {rental.client.full_name} | "
              f"{rental.car.brand} {rental.car.model} | "
              f"{rental.car.category.name} | {rental.total} KZT")
