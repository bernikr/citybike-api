from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.apis.citybikeAPI import CitybikeAccount, LoginError

login_bearer = HTTPBearer()


async def get_account(login_bearer: HTTPAuthorizationCredentials = Security(login_bearer)):
    try:
        return CitybikeAccount(session=login_bearer.credentials)
    except LoginError:
        raise HTTPException(status_code=401, detail="Login invalid")
