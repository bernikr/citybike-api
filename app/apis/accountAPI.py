from datetime import datetime, date
from typing import Union, Optional, List

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

COOKIE_NAME = 'a3990c06031454fe8851126e4477ea83'


class LoginError(IOError):
    pass


class Login(BaseModel):
    username: str
    password: str


class Ride(BaseModel):
    date: date
    start_station_name: str
    start_time: datetime
    end_station_name: str
    end_time: datetime
    price: float
    elevation: Optional[int]


class UserInfo(BaseModel):
    username: str
    name: str
    rides_this_year: int
    time_this_year: str
    last_ride_date: date
    credit: float
    email: str
    tel: str
    birthday: date
    address: str
    zip: str
    place: str
    country: str


class UphillChallenge(BaseModel):
    id: int
    description: str


class CitybikeAccount:
    def __init__(self, login: Union[Login, str]):
        if isinstance(login, Login):
            # start a request session to store the login cookie
            self.login_data = {"username": login.username, "password": login.password}
            self.s = requests.Session()
            self.login()
        elif isinstance(login, str):
            self.s = requests.Session()
            cookie_obj = requests.cookies.create_cookie(
                domain='citybikewien.at',
                name=COOKIE_NAME,
                value=login
            )
            self.s.cookies.set_cookie(cookie_obj)
            self.check_login()
        else:
            raise LoginError

    def login(self):
        login_data = self.login_data.copy()
        # get the hidden login fields needed to login
        frontpage = self.s.get("https://www.citybikewien.at/de")
        fp = BeautifulSoup(frontpage.content, 'html.parser')
        login = fp.find('form', id='mloginfrm')
        hiddeninputs = login.find_all('input', type='hidden')
        for i in hiddeninputs:
            login_data[i['name']] = i['value']

        # login to the site and save the cookie to the session
        login_url = "https://www.citybikewien.at/de/component/users/?task=user.login&Itemid=101"
        logedin = self.s.post(login_url, data=login_data)
        soup = BeautifulSoup(logedin.content, 'html.parser')
        user_name = soup.select(".user-name-data")
        if len(user_name) < 1:
            raise LoginError()

    def check_login(self):
        # check login to the site and save the cookie to the session
        login_url = "https://citybikewien.at/de/uebersicht"
        logedin = self.s.get(login_url)
        soup = BeautifulSoup(logedin.content, 'html.parser')
        user_name = soup.select(".user-name-data")
        if len(user_name) < 1:
            raise LoginError()

    def get_ride_count(self):
        # get the number of existing rows from the website
        page = self.s.get("https://www.citybikewien.at/de/meine-fahrten")
        soup = BeautifulSoup(page.content, 'html.parser')
        tab = soup.select('#content div + p')[0]
        return int(tab.get_text().split(' ')[2])

    def load_rides_page(self, starting_id):
        data_url = "https://www.citybikewien.at/de/meine-fahrten?start=" + str(starting_id)
        page = self.s.get(data_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.select('#content table tbody')[0]

        for row in table.find_all('tr'):
            r = []

            # go through every cell in a row
            for cell in row.find_all('td'):
                # check if if it is a 'normal' cell with only one data field
                children = cell.findChildren()
                if len(children) <= 1:
                    r.append(cell.get_text())
                else:
                    # if it contains a location and a date split it into two
                    r.append(children[0].get_text())
                    r.append(children[1].get_text() + ' ' + children[2].get_text())

            # Cutoff the Euro-sign from the price and the 'm' from the elevation
            r[5] = r[5][2:]
            if len(r) > 6:
                elevation = int(r[6][:-2])
            else:
                elevation = None

            # remove newlines
            r = [t.replace('\n', ' ').strip() for t in r]

            end_time = datetime.strptime(r[4], '%d.%m.%Y %H:%M')

            yield Ride(date=datetime.strptime(r[0], '%d.%m.%Y').date(),
                       start_station_name=r[1],
                       start_time=datetime.strptime(r[2], '%d.%m.%Y %H:%M'),
                       end_station_name=r[3],
                       end_time=end_time,
                       price=float(r[5].replace(',', '.')),
                       elevation=elevation
                       )

    def get_rides(self, yield_ride_count=False):
        ride_count = self.get_ride_count()

        if yield_ride_count:
            yield ride_count

        # load all pages and yield their contents
        for i in range(0, ride_count, 5):
            # read the rows
            count = 0
            for r in self.load_rides_page(i):
                count += 1
                yield r
            if count < 5:
                break

    def get_token(self):
        return self.s.cookies[COOKIE_NAME]

    def get_user_info(self):
        i = {}
        page = self.s.get("https://citybikewien.at/de/meine-daten")
        soup = BeautifulSoup(page.content, 'html.parser')
        i['name'] = soup.select(".user-name-data")[0].text[:-1]
        stats = soup.select(".user-stats-data")
        i['rides_this_year'] = int(stats[0].text)
        i['time_this_year'] = stats[1].text
        i['last_ride_date'] = datetime.strptime(stats[2].text, '%d.%m.%Y').date()
        i['credit'] = float(stats[3].text.replace(',', '.')[1:])

        d = {}
        for entry in soup.select(".data-list li"):
            spans = entry.select("span")
            if len(spans) == 2:
                d[spans[0].text.strip()[:-1]] = spans[1].text.strip()

        i['email'] = d['E-Mail']
        i['tel'] = d['Telefon']
        i['birthday'] = datetime.strptime(d['Geburtsdatum'], '%d.%m.%Y').date()
        i['address'] = d['Adresse']
        zip_and_place = d['Ort'].split(" ")
        i['zip'] = zip_and_place[0]
        i['place'] = " ".join(zip_and_place[1:])
        i['country'] = d['Land']
        i['username'] = d['Benutzername']
        return UserInfo.parse_obj(i)

    def get_uphill_challenges(self):
        page = self.s.get("https://citybikewien.at/de/uphillteam/144-verfuegbare-herausforderungen?all=1")
        soup = BeautifulSoup(page.content, 'html.parser')
        for item in soup.select(".panel-heading"):
            id = int(item.find("a").attrs['href'].split("/")[-1:][0])
            description = item.contents[0].strip()[:-2]
            yield UphillChallenge(id=id, description=description)
