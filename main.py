from fastapi import FastAPI
import uvicorn
import json
from model import Car
import aiofiles
import uuid

def create_data(path):
    with open(path, "w") as file:
        file.write(json.dumps([]))

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
async def remove_car(car_id: str):
    data = await db_cars.get_data()
    new_data = [car for car in data if not (car["id"] == car_id)]

    await db_cars.save_data(data=new_data)
    
    return {"status": "success"}


if __name__ == "__main__":
    create_data("cars.json")
    uvicorn.run(app, host="127.0.0.1", port=8000)