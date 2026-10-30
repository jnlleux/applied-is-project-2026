from datetime import date
from typing import Optional, List
from sqlalchemy import CheckConstraint
from sqlmodel import Field, Relationship, SQLModel

class Category(SQLModel, table=True):
    __table_args__ = (CheckConstraint("daily_rate > 0"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    daily_rate: int
    cars: List["Car"] = Relationship(back_populates="category")

class Car(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    brand: str
    model: str
    plate: str = Field(unique=True)
    category_id: int = Field(foreign_key="category.id")
    category: Category = Relationship(back_populates="cars")
    rentals: List["Rental"] = Relationship(back_populates="car")

class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    license_number: str = Field(unique=True)
    rentals: List["Rental"] = Relationship(back_populates="client")

class Rental(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint("end_date > start_date"),
        CheckConstraint("daily_rate > 0"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    car_id: int = Field(foreign_key="car.id")
    client_id: int = Field(foreign_key="client.id")
    start_date: date
    end_date: date
    daily_rate: int
    car: Car = Relationship(back_populates="rentals")
    client: Client = Relationship(back_populates="rentals")

    @property
    def total(self) -> int:
        return (self.end_date - self.start_date).days * self.daily_rate
