"""
The purpose of this script is to update the HTML of Degree Requirement for a calender year

Contributors:
Hao Wei Huang

Date April 22 2020
"""

import os
import urllib3
from bs4 import BeautifulSoup
from requests import get


url = "http://ugradcalendar.uwaterloo.ca/page/MATH-List-of-Academic-Programs-or-Plans"
root = "http://ugradcalendar.uwaterloo.ca/"


if __name__ == '__main__':
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'ProgramSpecs')

    #delete old files
    files = [f for f in os.listdir(path) if f.endswith(".html")]

    for f in files:
        os.remove(os.path.join(path, f))

    #fetch programs
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    data = BeautifulSoup(response.data, 'html.parser')

    table = data.find("span", class_="MainContent")
    links = table.find_all("a")
    for link in links:
        href = link['href']
        fileName = href.split("/")[-1]
        fileName = "/" + fileName + ".html"
        if "http" not in href:
            href = root + href
        print("Fetching " + href + "...")
        resp = get(href)
        with open(path + fileName, 'wb') as fOut:
            fOut.write(resp.content)