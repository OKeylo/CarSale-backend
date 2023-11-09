from fastapi import FastAPI, Depends
import uvicorn
import json
from model import Car
import aiofiles
import uuid
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
import os
from random import choice, randint, uniform, choices
import string

def create_cars() -> list[Car]:
    def create_gos_nomer(cars: list[Car]):
        cars_letters: str = "АВЕИКМНОРСТУХ"
        cars_numbers: str = "0123456789"

        while True:
            letters: str = ''.join(choices(cars_letters, k=3))
            numbers: str = ''.join(choices(cars_numbers, k=3))
            gos_nomer: str = letters[0] + numbers + letters[1:]

            if gos_nomer not in [car["gos_nomer"] for car in cars]:
                return gos_nomer

    cars: list[Car] = []
    car_marks: list[str] = ["BMW", "Audi", "Nissan", "Porsche", "Honda"] * 10
    car_year: list[int] = [randint(2010, 2023) for _ in range(50)]
    car_fuel: list[float] = [uniform(2.0, 4.0) for _ in range(50)]

    for i in range(len(car_marks)):
        car: Car = {
            "id": str(uuid.uuid4()),
            "gos_nomer": create_gos_nomer(cars),
            "mark": car_marks.pop(randint(0, len(car_marks) - 1)),
            "model": choice(string.ascii_uppercase) + str(randint(1, 9)),
            "year": car_year.pop(randint(0, len(car_year) - 1)),
            "fuel": round(car_fuel.pop(randint(0, len(car_fuel) - 1)), 1),
            "power": randint(100, 600),
            "price": randint(1000, 4000)*1000,
            "mileage": randint(20_000, 200_000),
        }
        cars.append(car)

    return cars

def create_data(path):
    if (not os.path.isfile(path)) or (os.stat(path).st_size == 0):
        data = []
        if path == "cars.json":
            data = create_cars()
        with open(path, "w") as file:
            file.write(json.dumps(data))

class DB_Cars:
    def __init__(self, file_path) -> None:
        self.path = file_path

    async def get_data(self):
        async with aiofiles.open(self.path, "r") as file:
            contents = await file.read()
        return json.loads(contents)
    
    async def save_data(self, data):
        async with aiofiles.open("cars.json", "w") as file:
            await file.write(json.dumps(data))
        return {"status": "success"}
    
class DB_Users:
    def __init__(self,file_path) -> None:
        self.path = file_path

    async def get_data(self):
        async with aiofiles.open(self.path, "r") as file:
            contents = await file.read()
        return json.loads(contents)
    
    async def save_data(self, data):
        async with aiofiles.open(self.path, "w") as file:
            await file.write(json.dumps(data))
        return {"status": "success"}
        

db_cars = DB_Cars("cars.json")
db_users = DB_Users("users.json")
security = HTTPBasic()
app = FastAPI()


@app.get("/cars", tags=["car"])
async def get_cars():
    data = await db_cars.get_data()

    return data


@app.post("/cars", tags=["car"])
async def add_car(car: Car):
    data = await db_cars.get_data()

    new_car: Car = {
        "id": str(uuid.uuid4()),
        "gos_nomer": car["gos_nomer"],
        "mark": car["mark"],
        "model": car["model"],
        "year": car["year"],
        "price": car["price"],
        "fuel": car["fuel"],
        "power": car["power"],
        "mileage": car["mileage"],
    }
    data.append(new_car)
    await db_cars.save_data(data=data)

    return {"status": "success"}


@app.delete("/cars/{car_id}", tags=["car"])
async def remove_car(car_id: str, credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    data = await db_cars.get_data()
    new_data = [car for car in data if not (car["id"] == car_id)]

    await db_cars.save_data(data=new_data)
    return {"username": credentials.username, "password": credentials.password}
    return {"status": "success"}


@app.post("/users", tags=["user"])
async def add_user(user):
    data = await db_users.get_data()

    data.append(user)
    await db_users.save_data(data=data)

    return {"status": "success"}

if __name__ == "__main__":
    create_data("cars.json")
    create_data("users.json")
    uvicorn.run(app, host="127.0.0.1", port=8000)