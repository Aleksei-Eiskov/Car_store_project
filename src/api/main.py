import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from sqlmodel import SQLModel, Session, create_engine, select
from .models import Brand, Car

DB_PATH = os.environ.get("DB_PATH", "data/car_store.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI(title="Car_store API", version="0.1.0")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Seed demo data if empty
    with Session(engine) as session:
        if not session.exec(select(Brand)).first():
            bmw = Brand(name="BMW")
            tesla = Brand(name="Tesla")
            session.add_all([bmw, tesla])
            session.commit()
            session.refresh(bmw); session.refresh(tesla)
            session.add_all([
                Car(name="Model 3", price=39999, brand_id=tesla.id),
                Car(name="Model Y", price=49999, brand_id=tesla.id),
                Car(name="320i", price=29999, brand_id=bmw.id),
            ])
            session.commit()

@app.get("/health")
def health():
    return {"status": "ok"}

# Brands CRUD
@app.post("/brands", response_model=Brand, status_code=201)
def create_brand(brand: Brand):
    with Session(engine) as session:
        brand.id = None
        session.add(brand)
        session.commit()
        session.refresh(brand)
        return brand

@app.get("/brands", response_model=List[Brand])
def list_brands():
    with Session(engine) as session:
        return list(session.exec(select(Brand)))

@app.get("/brands/{brand_id}", response_model=Brand)
def get_brand(brand_id: int):
    with Session(engine) as session:
        obj = session.get(Brand, brand_id)
        if not obj:
            raise HTTPException(404, "Brand not found")
        return obj

@app.patch("/brands/{brand_id}", response_model=Brand)
def patch_brand(brand_id: int, brand: Brand):
    with Session(engine) as session:
        obj = session.get(Brand, brand_id)
        if not obj:
            raise HTTPException(404, "Brand not found")
        if brand.name:
            obj.name = brand.name
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

@app.delete("/brands/{brand_id}", status_code=204)
def delete_brand(brand_id: int):
    with Session(engine) as session:
        obj = session.get(Brand, brand_id)
        if not obj:
            raise HTTPException(404, "Brand not found")
        session.delete(obj)
        session.commit()
        return

# Cars CRUD + filters
@app.post("/cars", response_model=Car, status_code=201)
def create_car(car: Car):
    with Session(engine) as session:
        if car.brand_id and not session.get(Brand, car.brand_id):
            raise HTTPException(400, "brand_id does not exist")
        car.id = None
        session.add(car)
        session.commit()
        session.refresh(car)
        return car

@app.get("/cars", response_model=List[Car])
def list_cars(
    brand_id: Optional[int] = None,
    q: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    with Session(engine) as session:
        stmt = select(Car)
        if brand_id is not None:
            stmt = stmt.where(Car.brand_id == brand_id)
        if q:
            like = f"%{q.lower()}%"
            # SQLite case-insensitive like by default
            stmt = stmt.where(Car.name.like(like))
        if min_price is not None:
            stmt = stmt.where(Car.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Car.price <= max_price)
        stmt = stmt.offset(offset).limit(limit)
        return list(session.exec(stmt))

@app.get("/cars/{car_id}", response_model=Car)
def get_car(car_id: int):
    with Session(engine) as session:
        obj = session.get(Car, car_id)
        if not obj:
            raise HTTPException(404, "Car not found")
        return obj

@app.patch("/cars/{car_id}", response_model=Car)
def patch_car(car_id: int, car: Car):
    with Session(engine) as session:
        obj = session.get(Car, car_id)
        if not obj:
            raise HTTPException(404, "Car not found")
        if car.name:
            obj.name = car.name
        if car.price is not None:
            obj.price = car.price
        if car.brand_id is not None:
            if not session.get(Brand, car.brand_id):
                raise HTTPException(400, "brand_id does not exist")
            obj.brand_id = car.brand_id
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

@app.delete("/cars/{car_id}", status_code=204)
def delete_car(car_id: int):
    with Session(engine) as session:
        obj = session.get(Car, car_id)
        if not obj:
            raise HTTPException(404, "Car not found")
        session.delete(obj)
        session.commit()
        return
