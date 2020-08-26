from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from app import security
from app.apis.accountAPI import CitybikeAccount, Login, UserInfo, Ride, UphillChallenge
from app.security import get_account
from app.service.account import get_rides_since

router = APIRouter()


@router.post("/token", response_model=str)
def get_token(login: Login):
    return security.get_token(login)


@router.get("/userinfo", response_model=UserInfo)
def get_userinfo(acc: CitybikeAccount = Depends(get_account)):
    return acc.get_user_info()


@router.get("/rides", response_model=List[Ride])
def api_get_rides(since: Optional[datetime] = None, acc: CitybikeAccount = Depends(get_account)):
    def generate():
        rides = get_rides_since(acc, since=since)

        yield '['
        first = True
        for ride in rides:
            if not first:
                yield ', '
            yield ride.json()
            first = False
        yield ']'

    return StreamingResponse(generate(), media_type="application/json")


@router.get("/uphillchallenges", response_model=List[UphillChallenge])
def get_uphill_challenges(acc: CitybikeAccount = Depends(get_account)):
    return acc.get_uphill_challenges()
