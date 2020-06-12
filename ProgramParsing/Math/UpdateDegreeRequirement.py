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


url_plans = "http://ugradcalendar.uwaterloo.ca/page/MATH-List-of-Academic-Programs-or-Plans"
root = "http://ugradcalendar.uwaterloo.ca/"

url_minor = "https://ugradcalendar.uwaterloo.ca/group/MATH-Academic-Plans-and-Requirements"

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

def fetch_math_faculty_minor(path):
    """
             path: str
             Script to download all html pages for minors in Faculty of Math
             return:
    """
    link_to_ignore = ["Academic Plans and Requirements", "Degree Requirements for all Math students",
                      "Plans for Students outside the Mathematics Faculty", "Software Engineering"]

    # fetch programs
    http = urllib3.PoolManager()
    response = http.request('GET', url_minor)
    data = BeautifulSoup(response.data, 'html.parser')

    table = data.find_all("a", class_="Level3")

    for major in table:
        if str(major.text) not in link_to_ignore:
            link = root + major["href"]
            major_reponse = http.request('GET', link)
            major_data = BeautifulSoup(major_reponse.data, 'html.parser')
            major_table = major_data.find_all("a", class_="Level3Group")
            print("Looking for minors in {}...".format(str(major['href'])))
            for l in major_table:
                if "minor" in str(l.text).lower():
                    print("Fetching {}...".format(str(l.text)))
                    href = root + l['href']
                    fileName = href.split("/")[-1]
                    fileName = "/" + fileName + ".html"
                    resp = get(href)
                    with open(path + fileName, 'wb') as fOut:
                        fOut.write(resp.content)


if __name__ == '__main__':
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'ProgramSpecs')

    # check if folder exist
    if os.path.isdir(path):
        # delete old files
        files = [f for f in os.listdir(path) if f.endswith(".html")]

        for f in files:
            os.remove(os.path.join(path, f))
    else:
        os.mkdir(path)

    fetch_degree_req(path)
    fetch_math_faculty_minor(path)
