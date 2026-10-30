from datetime import date
from sqlmodel import Session, select
from app.database.db import engine, init_db
from app.database.models import Category, Car, Client, Rental

def seed():
    init_db()
    with Session(engine) as session:
        if any(session.exec(select(m)).first() for m in (Category, Car, Client, Rental)):
            print("Database is not empty; seed skipped.")
            return
        categories = [Category(name=n, daily_rate=r) for n, r in
                      [("Эконом", 15000), ("Комфорт", 22000), ("Бизнес", 35000)]]
        cars = [Car(brand=b, model=m, plate=p, category=c) for b,m,p,c in [
            ("Hyundai", "Accent", "DEMO-001", categories[0]),
            ("Toyota", "Camry", "DEMO-002", categories[1]),
            ("Kia", "K5", "DEMO-003", categories[2])]]
        clients = [Client(full_name=f"Учебный клиент {i}", license_number=f"TEST-{i:03}")
                   for i in range(1,4)]
        rentals = [Rental(car=cars[i], client=clients[i], start_date=date(2026,10,1+i),
                          end_date=date(2026,10,4+i), daily_rate=categories[i].daily_rate)
                   for i in range(3)]
        session.add_all(categories + cars + clients + rentals)
        session.commit()
        print("Seed complete: category=3 car=3 client=3 rental=3")

if __name__ == "__main__":
    seed()
