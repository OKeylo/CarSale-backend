from fastapi import FastAPI
import json
from model import Car


app = FastAPI()


@app.get("/cars")
def get_cars():
    with open("cars.json") as file:
        data = json.load(file)["data"]
    return {"cars": data}


@app.post("/cars")
def add_car(car: Car):
    try:
        with open("cars.json", "r") as file:
            data = json.load(file)
            data["data"].append(car)
        with open("cars.json", "w") as file:
            json.dump(data, file)
    except FileNotFoundError or json.decoder.JSONDecodeError:
        with open("cars.json", "w") as file:
            json.dump({"data": [car]}, file)
    return {"status": "success"}
