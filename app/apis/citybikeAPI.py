from datetime import datetime

import requests
from bs4 import BeautifulSoup

from app.entities import Ride


class LoginError(IOError):
    pass


class CitybikeAccount:
    def __init__(self, username=None, password=None, session=None):
        if username is not None and password is not None:
            # start a request session to store the login cookie
            self.login_data = {"username": username, "password": password}
            self.s = requests.Session()
            self.login()
        elif session is not None:
            self.s = requests.Session()
            cookie_obj = requests.cookies.create_cookie(
                domain='citybikewien.at',
                name='a3990c06031454fe8851126e4477ea83',
                value=session
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

    def load_page(self, starting_id, since=datetime.min):
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
            r[6] = r[6][:-2]

            # remove newlines
            r = [t.replace('\n', ' ').strip() for t in r]

            end_time = datetime.strptime(r[4], '%d.%m.%Y %H:%M')

            if end_time > since:
                yield Ride(date=datetime.strptime(r[0], '%d.%m.%Y').date(),
                           start_station_name=r[1],
                           start_time=datetime.strptime(r[2], '%d.%m.%Y %H:%M'),
                           end_station_name=r[3],
                           end_time=end_time,
                           price=float(r[5].replace(',', '.')),
                           elevation=int(r[6])
                           )
            else:
                break

    def get_rides(self, since=None, yield_ride_count=False):
        if since is None:
            since = datetime.min

        ride_count = self.get_ride_count()

        if yield_ride_count:
            yield ride_count

        # load all pages and yield their contents
        for i in range(0, ride_count, 5):
            # read the rows
            count = 0
            for r in self.load_page(i, since=since):
                count += 1
                yield r
            if count < 5:
                break
