from fastapi import FastAPI
import json
from model import Car
import aiofiles
import uuid


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
        

db_cars = DB_Cars("cars.json")
app = FastAPI()


@app.get("/cars")
async def get_cars():
    data = await db_cars.get_data()

    return data


@app.post("/cars")
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


@app.delete("/cars/{car_id}")
def remove_car(car_id: str):
    with open("cars.json", "r") as file:
        data: list[Car] = json.load(file)
        new_data = [car for car in data["data"] if not (car["id"] == car_id)]
        data["data"] = new_data
    with open("cars.json", "w") as file:
        json.dump(data, file)
    return {"status": "success"}