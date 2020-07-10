"""
The purpose of this script is to update the HTML of Degree Requirement for a calender year
"""

import os
import urllib3
from bs4 import BeautifulSoup
from requests import get


url_plans = "https://ugradcalendar.uwaterloo.ca/group/ENG-BASc-and-BSE-Specific-Degree-Requirements"
root = "http://ugradcalendar.uwaterloo.ca/"

def fetch_degree_req(path):
    """
         path: str
         Script to download all html pages for degree req
         return:
    """

    #fetch programs
    http = urllib3.PoolManager()
    response = http.request('GET', url_plans)
    data = BeautifulSoup(response.data, 'html.parser')

    Engineering = ["Architectural Engineering", "Biomedical Engineering", "Chemical Engineering", "Civil Engineering",
                   "Computer Engineering", "Electrical Engineering", "Environmental Engineering", "Geological Engineering",
                   "Management Engineering", "Mechanical Engineering", "Mechatronics Engineering", "Nanotechnology Engineering",
                   "Software Engineering", "Systems Design Engineering"]

    majors_links = data.find_all("a", class_="Level2Group")
    for major in majors_links:

        if (str(major.text) not in Engineering):
            continue
        print("Fetching {}...".format(str(major.text)))
        href = root + major['href']
        fileName = href.split("/")[-1]
        fileName = "/" + fileName + ".html"
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

    fetch_degree_req(path)
