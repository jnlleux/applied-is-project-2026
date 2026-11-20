from datetime import date
from pydantic import BaseModel, Field, ConfigDict, model_validator

class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
class CategoryCreate(Input):
    name: str = Field(min_length=1, max_length=100)
    daily_rate: int = Field(gt=0)
class CarCreate(Input):
    brand: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    plate: str = Field(min_length=1, max_length=30)
    category_id: int = Field(gt=0)
class ClientCreate(Input):
    full_name: str = Field(min_length=1, max_length=200)
    license_number: str = Field(min_length=1, max_length=50)
class RentalCreate(Input):
    car_id: int = Field(gt=0)
    client_id: int = Field(gt=0)
    start_date: date
    end_date: date
    daily_rate: int = Field(gt=0)
    @model_validator(mode="after")
    def dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("Дата окончания должна быть позже начала")
        return self

from pydantic import create_model
from typing import Annotated

def patch_model(name, source):
    fields = {}
    for key, field in source.model_fields.items():
        fields[key] = (Annotated[field.annotation | None, *field.metadata] if field.metadata else field.annotation | None, None)
    return create_model(name, __base__=Input, **fields)
CategoryPatch = patch_model("CategoryPatch", CategoryCreate)
CarPatch = patch_model("CarPatch", CarCreate)
ClientPatch = patch_model("ClientPatch", ClientCreate)
RentalPatch = patch_model("RentalPatch", RentalCreate)
