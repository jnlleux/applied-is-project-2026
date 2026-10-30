import os
import tempfile
from pathlib import Path
from datetime import date
with tempfile.TemporaryDirectory() as directory:
    os.environ['DATABASE_URL'] = 'sqlite:///' + str(Path(directory) / 'test.db')
    from sqlalchemy.exc import IntegrityError
    from sqlmodel import Session, select
    from app.database.db import engine
    from app.database.models import Category, Car, Client, Rental
    from seed import seed
    seed()
    seed()
    with Session(engine) as session:
        for model in (Category, Car, Client, Rental):
            assert len(session.exec(select(model)).all()) == 3
        rental = session.exec(select(Rental)).first()
        assert rental.car.category.name == 'Эконом'
        assert rental.client.full_name == 'Учебный клиент 1'
        assert rental.total == 45000
    invalid = [Category(name='Bad', daily_rate=-1),
        Car(brand='Test', model='Test', plate='BAD', category_id=999),
        Client(full_name='Duplicate', license_number='TEST-001'),
        Rental(car_id=1, client_id=1, start_date=date(2026,10,5), end_date=date(2026,10,4), daily_rate=1)]
    for record in invalid:
        with Session(engine) as session:
            session.add(record)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
            else:
                raise AssertionError('Invalid record accepted')
    engine.dispose()
print('PASS: counts, repeated seed, relationships, total, positive rate, FK, unique license, dates')
