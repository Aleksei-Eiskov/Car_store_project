from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Brand(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    cars: List["Car"] = Relationship(back_populates="brand")

class Car(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float
    brand_id: Optional[int] = Field(default=None, foreign_key="brand.id")
    brand: Optional[Brand] = Relationship(back_populates="cars")
