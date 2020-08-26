from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from app.apis.citybikeAPI import CitybikeAccount
from app.entities import Ride
from app.security import get_account

router = APIRouter()


@router.get('/rides', response_model=List[Ride])
def hello_world(since: Optional[datetime] = None, acc: CitybikeAccount = Depends(get_account)):
    def generate():
        rides = acc.get_rides(since=since)

        yield '['
        first = True
        for ride in rides:
            if not first:
                yield ', '
            yield ride.json()
            first = False
        yield ']'

    return StreamingResponse(generate(), media_type="application/json")
