from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app.readme_generator import get_description
from app.routers import account, stations, stats

app = FastAPI(
    title="Inofficial Citybike Vienna API",
    description=get_description(),
    version="0.3.0",
)

app.include_router(stations.router, prefix="/stations", tags=["Stations"])
app.include_router(stats.router, prefix="/stats", tags=["Statistics"])
app.include_router(account.router, prefix="/account", tags=["Account"])


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
