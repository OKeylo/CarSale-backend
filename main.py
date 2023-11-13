from fastapi import FastAPI, Depends, HTTPException, status
import uvicorn
import json
from model import Car, User, UserLogin, UserRegister
import aiofiles
import uuid
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
import os
from random import choice, randint, uniform, choices
import string
import secrets
from fastapi.middleware.cors import CORSMiddleware
import base64

def create_password():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(8))
    return password

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def check_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    data: list[User] = await db_users.get_data()
    username_decoded = base64.b64decode(credentials.username).decode('utf-8')
    password_decoded = base64.b64decode(credentials.password).decode('utf-8')

    user: User = dict(*[i for i in data if i["username"] == username_decoded])
    if user and user["password"] == password_decoded:
        return True
    
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )


@app.get("/cars", tags=["car"])
async def get_cars():
    data = await db_cars.get_data()

    return data


@app.get("/cars/{user_id}", tags=["car"])
async def get_cars_by_user_id(user_id: str):
    data = await db_cars.get_data()

    user_data = [car for car in data if car["author_id"] == user_id]

    return user_data


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


@app.delete("/cars/{car_id}", tags=["car"], dependencies=[Depends(check_user)])
async def remove_car(car_id: str):
    data = await db_cars.get_data()
    new_data = [car for car in data if not (car["id"] == car_id)]

    await db_cars.save_data(data=new_data)
    return {"status": "success"}


@app.post("/user/signup", tags=["user"])
async def add_user(user: UserRegister):
    data = await db_users.get_data()

    check_username_exist = dict(*[i for i in data if i["username"] == user["username"] or i["phone"] == user["phone"]])
    if check_username_exist:
        raise HTTPException(
        status_code=406,
        detail="Пользователь с таким именем или телефоном уже существует!"
        )

    new_user: User = {
        "id": str(uuid.uuid4()),
        "username": user["username"],
        "password": user["password"],
        "phone": user["phone"],
    }
    data.append(new_user)

    await db_users.save_data(data=data)
    return {"status": "success"}


@app.post("/user/login", tags=["user"])
async def user_login(user: UserLogin):
    data = await db_users.get_data()

    user_bd: User = dict(*[i for i in data if i["username"] == user["username"]])
    if user_bd and user_bd["password"] == user["password"]:
        return True
    
    raise HTTPException(
        status_code=406,
        detail="Неверный логин или пароль!"
    )

@app.get("/user/{user_id}", tags=["user"])
async def get_user_by_id(user_id: str):
    data = await db_users.get_data()

    user: User = dict(*[i for i in data if i["id"] == user_id])
    if user:
        return user
    
    raise HTTPException(
        status_code=406,
        detail="Не найдено пользователя с таким id!"
    )

@app.get("/user/me/{user_username}", tags=["user"])
async def get_user_by_username(user_username: str):
    data = await db_users.get_data()

    user: User = dict(*[i for i in data if i["username"] == user_username])
    if user:
        return user
    
    raise HTTPException(
        status_code=406,
        detail="Не найдено пользователя с таки именем!!"
    )

if __name__ == "__main__":
    create_data("cars.json")
    create_data("users.json")
    uvicorn.run(app, host="127.0.0.1", port=8000)