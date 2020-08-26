import datetime
import logging
from typing import Tuple, List, Optional

import requests
import xmltodict

from app.entities import StationInfo, Location, StationDistanceInfo

logger = logging.getLogger(__name__)

station_cache = []
last_cached = datetime.datetime.min
cache_time = datetime.timedelta(seconds=10)


def station_dict_to_model(s: dict) -> StationInfo:
    return StationInfo(
        id=int(s['id']),
        name=s['name'],
        free_boxes=int(s['free_boxes']),
        free_bikes=int(s['free_bikes']),
        loc=Location(
            lat=s['latitude'],
            lon=s['longitude']
        )
    )


def get_all_stations() -> List[StationInfo]:
    logger.info("get_all_stations")
    global station_cache, last_cached, cache_time
    if datetime.datetime.now() > last_cached + cache_time:
        r = requests.get('http://dynamisch.citybikewien.at/citybike_xml.php')
        logger.info("Request Station Data from API")
        station_cache = [station_dict_to_model(s) for s in xmltodict.parse(r.content)['stations']['station']]
        last_cached = datetime.datetime.now()
    return station_cache


def get_station_by_id(id: int) -> Optional[StationInfo]:
    logger.info("get_station_by_id")
    station = [s for s in get_all_stations() if s.id == id]
    if len(station) == 1:
        return station[0]
    else:
        return None


def get_nearest_stations(loc: Location, n: int = None) -> List[StationDistanceInfo]:
    logger.info("get_nearest_stations")
    stations = get_all_stations()
    station_distance_infos = [StationDistanceInfo(station=s, distance=s.loc.distance(loc)) for s in stations]
    station_distance_infos = sorted(station_distance_infos, key=lambda x: x.distance)
    if n is not None:
        station_distance_infos = station_distance_infos[:n]
    return station_distance_infos
