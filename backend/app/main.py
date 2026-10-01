from fastapi import FastAPI

app = FastAPI(title="Navgaon API")


@app.get("/")
def root():
    return {"message": "Welcome to Navgaon"}