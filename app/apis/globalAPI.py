import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel


class GlobalStats(BaseModel):
    km_year: int
    km_day: int
    bikes_in_use: int


def get_global_stats():
    page = requests.get("https://citybikewien.at/de/")
    soup = BeautifulSoup(page.content, 'html.parser')
    s = [int(a.text.replace(".","")) for a in soup.select(".stats-list li .stats-num")]
    return GlobalStats(km_year=s[0], km_day=s[1], bikes_in_use=s[2])
