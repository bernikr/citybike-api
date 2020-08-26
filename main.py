import json
from datetime import datetime, date
from json import JSONEncoder
from typing import Optional, List, Tuple

import uvicorn as uvicorn
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.responses import StreamingResponse

import app.apis.stationAPI as StationAPI
from app.apis.citybikeAPI import CitybikeAccount, LoginError
from app.entities import Station, Location

app = FastAPI()


login_bearer = HTTPBearer()


async def get_account(login_bearer: HTTPAuthorizationCredentials = Security(login_bearer)):
    try:
        return CitybikeAccount(session=login_bearer.credentials)
    except LoginError:
        raise HTTPException(status_code=401, detail="Login invalid")


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


@app.get('/rides')
def hello_world(since: Optional[datetime] = None, acc: CitybikeAccount = Depends(get_account)):
    def generate():
        rides = acc.get_rides(yield_ride_count=True, since=since)

        yield '{"count": ' + str(next(rides)) + ",\n"

        yield '"rides": [\n'
        first = True
        for ride in rides:
            if not first:
                yield ',\n'
            yield json.dumps(ride, cls=DateTimeEncoder)
            first = False
        yield '\n]}'

    return StreamingResponse(generate(), media_type="application/json")


class DateTimeEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%dT%H:%M:%S")
        if isinstance(o, date):
            return o.strftime("%Y-%m-%d")


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
