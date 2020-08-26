from geopy import distance
from pydantic import BaseModel


class Location(BaseModel):
    lat: float
    lon: float

    def distance(self, other_loc):
        return distance.distance((self.lat, self.lon), (other_loc.lat, other_loc.lon)).meters


class Station(BaseModel):
    id: int
    name: str
    free_boxes: int
    free_bikes: int
    loc: Location
