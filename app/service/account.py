from datetime import datetime

from app.apis.accountAPI import CitybikeAccount


def get_rides_since(acc: CitybikeAccount, since: datetime = datetime.min):
    for r in acc.get_rides():
        if r.start_time >= since:
            yield r
        else:
            break
