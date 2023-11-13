from typing_extensions import TypedDict


class Car(TypedDict):
    id: str
    author_id: str
    mark: str
    model: str
    year: int
    price: int
    fuel: float
    power: int
    mileage: int

class addCar(TypedDict):
    author_id: str
    mark: str
    model: str
    year: int
    price: int
    fuel: float
    power: int
    mileage: int


class User(TypedDict):
    id: str
    username: str
    password: str
    phone: str

class UserLogin(TypedDict):
    username: str
    password: str

class UserRegister(TypedDict):
    username: str
    password: str
    phone: str