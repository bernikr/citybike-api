import json
from datetime import datetime, date
from json import JSONEncoder
from typing import Optional

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from app.apis.citybikeAPI import CitybikeAccount
from app.security import get_account

router = APIRouter()


@router.get('/rides')
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

