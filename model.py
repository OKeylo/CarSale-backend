from typing_extensions import TypedDict


class Car(TypedDict):
    id: str
    gos_nomer: str
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
    email: str
    password: str
