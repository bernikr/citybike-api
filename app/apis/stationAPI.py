import datetime
import logging
from typing import Tuple, List, Optional

import requests
import xmltodict

from app.entities import Station, Location

logger = logging.getLogger(__name__)

station_cache = []
last_cached = datetime.datetime.min
cache_time = datetime.timedelta(seconds=10)


def station_dict_to_model(s: dict) -> Station:
    return Station(
        id=int(s['id']),
        name=s['name'],
        free_boxes=int(s['free_boxes']),
        free_bikes=int(s['free_bikes']),
        loc=Location(
            lat=s['latitude'],
            lon=s['longitude']
        )
    )


def get_all_stations() -> List[Station]:
    logger.info("get_all_stations")
    global station_cache, last_cached, cache_time
    if datetime.datetime.now() > last_cached + cache_time:
        r = requests.get('http://dynamisch.citybikewien.at/citybike_xml.php')
        logger.info("Request Station Data from API")
        station_cache = [station_dict_to_model(s) for s in xmltodict.parse(r.content)['stations']['station']]
        last_cached = datetime.datetime.now()
    return station_cache


def get_station_by_id(id: int) -> Optional[Station]:
    logger.info("get_station_by_id")
    station = [s for s in get_all_stations() if s.id == id]
    if len(station) == 1:
        return station[0]
    else:
        return None


def get_nearest_stations(loc: Location, n: int = None) -> List[Tuple[Station, int]]:
    logger.info("get_nearest_stations")
    stations = get_all_stations()
    station_distance_pairs = [(s, s.loc.distance(loc)) for s in stations]
    station_distance_pairs = sorted(station_distance_pairs, key=lambda x: x[1])
    if n is not None:
        station_distance_pairs = station_distance_pairs[:n]
    return station_distance_pairs
