from fastapi import FastAPI

app = FastAPI()

@app.get("/cars")
def get_cars():
    return {"cars": []}