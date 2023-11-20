from fastapi import FastAPI, Depends, HTTPException, status
import uvicorn
import json
from model import Car, User, UserLogin, UserRegister, addCar
import aiofiles
import uuid
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
import os
from random import choice, randint, uniform, choices
import string
from fastapi.middleware.cors import CORSMiddleware
import base64

def create_cars(users: list[User]) -> list[Car]:
    car_marks: list[str] = ["BMW", "Audi", "Nissan", "Porsche", "Honda", "Mazda", "Lada"]
    
    cars: list[Car] = []
    for _ in range(30):
        car: Car = {
            "id": str(uuid.uuid4()),
            "author_id": choice(users)["id"],
            "mark": choice(car_marks),
            "model": choice(string.ascii_uppercase) + str(randint(1, 9)),
            "year": randint(2000, 2023),
            "fuel": round(uniform(2.0, 4.0), 1),
            "power": randint(100, 600),
            "price": randint(1000, 4000)*1000,
            "mileage": randint(20_000, 200_000),
        }
        cars.append(car)

    return cars

def create_users() -> list[User]:
    def create_username(users: list[User]):
        vowels_lower = "aeiou"
        cons_lower = "bcdfghjklmnpqrstvwxyz"
        cons_upper = "BCDFGHJKLMNPQRSTVWXYZ"

        while True:
            username: str = f"{choice(cons_upper)}{choice(vowels_lower)}{choice(cons_lower)}{choice(vowels_lower)}"
            if username not in [user["username"] for user in users]:
                return username
    
    def create_password():
        alphabet = string.ascii_letters + string.digits
        password = ''.join(choices(alphabet, k=4))
        return password
    
    def create_phone(users: list[User]):
        digits = string.digits
        while True:
            phone: str = f"+{choice([7,8])} {''.join(choices(digits, k=3))} {''.join(choices(digits, k=3))}-{''.join(choices(digits, k=2))}-{''.join(choices(digits, k=2))}"
            if phone not in [user["phone"] for user in users]:
                return phone
    
    users: list[User] = []
    for _ in range(5):
        user: User = {
            "id": str(uuid.uuid4()),
            "username": create_username(users),
            "password": create_password(),
            "phone": create_phone(users)
        }
        users.append(user)

    return users

def create_data(path, data=[]):
    if (not os.path.isfile(path)) or (os.stat(path).st_size == 0):
        if path == "cars.json" and data:
            data = create_cars(users=data)
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

    return data[::-1]


@app.get("/cars/{user_id}", tags=["car"])
async def get_cars_by_user_id(user_id: str):
    data = await db_cars.get_data()

    user_data = [car for car in data if car["author_id"] == user_id][::-1]

    return user_data


@app.post("/cars", tags=["car"], dependencies=[Depends(check_user)])
async def add_car(car: addCar):
    data = await db_cars.get_data()

    new_car: Car = {
        "id": str(uuid.uuid4()),
        "author_id": car["author_id"],
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
    users: list[User] = create_users()
    create_data("users.json", data=users)
    create_data("cars.json", data=users)
    uvicorn.run(app, host="127.0.0.1", port=8000)