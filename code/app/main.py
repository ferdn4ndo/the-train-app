from fastapi import FastAPI, Header, HTTPException

from api.routers import simulations, trains, routes

app = FastAPI()


@app.get("/")
def read_root():
    return {'foo5': 'bar'}


async def get_token_header(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


app.include_router(simulations.router)
app.include_router(trains.router)
app.include_router(routes.router)
