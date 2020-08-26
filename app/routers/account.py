from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from app import security
from app.apis.citybikeAPI import CitybikeAccount, Login, UserInfo
from app.entities import Ride
from app.security import get_account

router = APIRouter()


@router.post("/token", response_model=str)
def get_token(login: Login):
    return security.get_token(login)


@router.get("/rides", response_model=List[Ride])
def get_rides(since: Optional[datetime] = None, acc: CitybikeAccount = Depends(get_account)):
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


@router.get("/userinfo", response_model=UserInfo)
def get_userinfo(acc: CitybikeAccount = Depends(get_account)):
    return acc.get_user_info()
