from typing import List, Optional, Tuple

from fastapi import APIRouter, HTTPException

from app.apis import stationAPI
from app.entities import Location
from app.apis.stationAPI import StationInfo, StationDistanceInfo

router = APIRouter()


@router.get("", response_model=List[StationInfo])
def get_all_stations():
    return stationAPI.get_all_stations()


@router.get("/{station_id}", response_model=StationInfo)
def read_item(station_id: int):
    station = stationAPI.get_station_by_id(station_id)
    if station is None:
        raise HTTPException(status_code=404, detail="Station not found")
    return station


@router.post("/near", response_model=List[StationDistanceInfo])
def get_nearest_station(loc: Location, limit: Optional[int] = None):
    return stationAPI.get_nearest_stations(loc, limit)
