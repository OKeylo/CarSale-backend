from fastapi import FastAPI
import json
from model import Car


app = FastAPI()


@app.get("/cars")
def get_cars():
    try:
        with open("cars.json") as file:
            data = json.load(file)["data"]
        return {"cars": data}
    except:
        return {"cars": []}


@app.post("/cars")
def add_car(car: Car):
    try:
        with open("cars.json", "r") as file:
            data = json.load(file)
            data["data"].append(car)
        with open("cars.json", "w") as file:
            json.dump(data, file)
    except json.decoder.JSONDecodeError:
        with open("cars.json", "w") as file:
            json.dump({"data": [car]}, file)
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