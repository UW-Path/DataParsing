"""
The purpose of this script is to update the HTML of Degree Requirement for a calender year

Contributors:
Hao Wei Huang
"""

import os
import urllib3
from bs4 import BeautifulSoup
from requests import get


url_plans = "https://ugradcalendar.uwaterloo.ca/group/SCI-Science-Academic-Programs-and-Plans1"
root = "http://ugradcalendar.uwaterloo.ca/"

url_minor = "https://ugradcalendar.uwaterloo.ca/group/SCI-Minors-Options-Joint-Progs-Internat-Partner"

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

    majors_links = data.find_all("a", class_="Level2Group")
    for major in majors_links:
        link = root + major["href"]
        if "optometry" in major.text.lower() or "pharmacy" in major.text.lower():
            continue
        major_reponse = http.request('GET', link)
        major_data = BeautifulSoup(major_reponse.data, 'html.parser')
        major_table = major_data.find_all("a", class_="Level3Group")
        print("Looking for minors in {}...".format(str(major['href'])))
        for l in major_table:
            if "co-operative" in str(l.text).lower() or "overview" in str(l.text).lower():
                continue

            print("Fetching {}...".format(str(l.text)))
            href = root + l['href']
            fileName = href.split("/")[-1]
            fileName = "/" + fileName + ".html"
            resp = get(href)
            with open(path + fileName, 'wb') as fOut:
                fOut.write(resp.content)

def fetch_faculty_minor(path):
    """
             path: str
             Script to download all html pages for minors in Faculty of Math
             return:
    """
    link_to_ignore = ["Academic Plans and Requirements", "Degree Requirements for all Math students"]

    # fetch programs
    http = urllib3.PoolManager()
    response = http.request('GET', url_minor)
    data = BeautifulSoup(response.data, 'html.parser')

    table = data.find_all("a", class_="Level3Group")

    for minor in table:
        if str(minor.text) not in link_to_ignore:
            print("Fetching {}...".format(str(minor.text)))
            href = root + minor['href']
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
    fetch_faculty_minor(path)
