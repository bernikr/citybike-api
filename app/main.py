from fastapi import FastAPI
from starlette.responses import RedirectResponse

from .routers import stations, rides

app = FastAPI()
app.include_router(stations.router, prefix="/stations", tags=["Stations"])
app.include_router(rides.router, prefix="/rides", tags=["Rides"])


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
