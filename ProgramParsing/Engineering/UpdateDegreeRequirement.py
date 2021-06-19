"""
The purpose of this script is to update the HTML of Degree Requirement for a calender year
"""

import os
import urllib3
from bs4 import BeautifulSoup
from requests import get
from datetime import datetime

url_plans = "https://ugradcalendar.uwaterloo.ca/group/ENG-BASc-and-BSE-Specific-Degree-Requirements/?ActiveDate=9/1/"
root = "http://ugradcalendar.uwaterloo.ca/"

def fetch_degree_req(path, year):
    """
         path: str
         Script to download all html pages for degree req
         return:
    """

    #fetch programs
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    response = http.request('GET', url_plans + str(year))
    data = BeautifulSoup(response.data, 'html.parser')

    Engineering = ["Architectural Engineering", "Biomedical Engineering",
                   "Chemical Engineering", "Civil Engineering",
                   "Computer Engineering", "Computer Engineering and Electrical Engineering",
                   "Electrical Engineering", "Environmental Engineering",
                   "Geological Engineering", "Management Engineering",
                   "Mechanical Engineering", "Mechatronics Engineering",
                   "Nanotechnology Engineering", "Software Engineering",
                   "Systems Design Engineering"]

    majors_links = data.find_all("a", class_="Level2Group")
    for major in majors_links:

        if (str(major.text) not in Engineering):
            continue
        print("Fetching {}...".format(str(major.text)))
        href = root + major['href'] + '/?ActiveDate=9/1/' + str(year)
        fileName = href.split("/")[-4]
        a_year = str(year % 1000) + '-' + str(year % 1000 + 1)
        fileName = "/" + a_year + '-' + fileName + ".html"
        resp = get(href)
        with open(path + fileName, 'wb') as fOut:
            fOut.write(resp.content)

if __name__ == '__main__':
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'Specs')

    # check if folder exist
    if os.path.isdir(path):
        # delete old files
        files = [f for f in os.listdir(path) if f.endswith(".html")]

        for f in files:
            os.remove(os.path.join(path, f))
    else:
        os.mkdir(path)

    cur_year = datetime.today().year
    for year in range(cur_year - 5, cur_year + 1):
        fetch_degree_req(path, year)
