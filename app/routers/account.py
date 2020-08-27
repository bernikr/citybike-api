from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import StreamingResponse, HTMLResponse

from app import security
from app.apis.accountAPI import CitybikeAccount, Login, UserInfo, Ride, UphillChallenge, CurrentUphillChallenge
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
def get_all_rides(since: Optional[datetime] = None, acc: CitybikeAccount = Depends(get_account)):
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
def get_available_uphill_challenges(acc: CitybikeAccount = Depends(get_account)):
    return acc.get_uphill_challenges()


@router.get("/uphillchallenges/current", response_model=Optional[CurrentUphillChallenge])
def get_current_uphill_challenge(acc: CitybikeAccount = Depends(get_account)):
    return acc.get_current_uphill_challenge()


@router.delete("/uphillchallenges/current")
def cancel_current_uphill_challenge(acc: CitybikeAccount = Depends(get_account)):
    acc.cancel_current_uphill_challenge()


@router.get("/uphillchallenges/{challenge_id}", response_class=HTMLResponse)
def get_uphill_challenge_details(challenge_id: int, acc: CitybikeAccount = Depends(get_account)):
    details = acc.get_uphill_challenge_detail(challenge_id)
    if details is None:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return details


@router.post("/uphillchallenges/{challenge_id}")
def accept_uphill_challenge(challenge_id: int, acc: CitybikeAccount = Depends(get_account)):
    acc.accept_uphill_challenge(challenge_id)
