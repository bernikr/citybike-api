from typing import Optional, List, Tuple

import uvicorn as uvicorn
from fastapi import FastAPI, HTTPException

import app.apis.stationAPI as StationAPI
from app.service.entities import Station, Location

app = FastAPI()


@app.get("/stations", response_model=List[Station])
def get_all_stations():
    return StationAPI.get_all_stations()


@app.get("/stations/{station_id}", response_model=Station)
def read_item(station_id: int):
    station = StationAPI.get_station_by_id(station_id)
    if station is None:
        raise HTTPException(status_code=404, detail="Station not found")
    return station


@app.post("/stations/near", response_model=List[Tuple[Station, int]])
def get_nearest_station(loc: Location, limit: Optional[int] = None):
    return StationAPI.get_nearest_stations(loc, limit)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
