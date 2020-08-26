from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app.routers import account, stations

app = FastAPI()
app.include_router(stations.router, prefix="/stations", tags=["Stations"])
app.include_router(account.router, prefix="/account", tags=["Account"])


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
