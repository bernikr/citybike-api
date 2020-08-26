from datetime import datetime, date

from geopy import distance
from pydantic import BaseModel


class Location(BaseModel):
    lat: float
    lon: float

    def distance(self, other_loc):
        return distance.distance((self.lat, self.lon), (other_loc.lat, other_loc.lon)).meters


class StationInfo(BaseModel):
    id: int
    name: str
    free_boxes: int
    free_bikes: int
    loc: Location


class StationDistanceInfo(BaseModel):
    station: StationInfo
    distance: float


class Ride(BaseModel):
    date: date
    start_station_name: str
    start_time: datetime
    end_station_name: str
    end_time: datetime
    price: float
    elevation: int