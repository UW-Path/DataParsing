"""
The purpose of this script is to update the HTML of Degree Requirement for a calender year
"""

import os
import urllib3
from bs4 import BeautifulSoup
from requests import get
from datetime import datetime


url_plans = "https://ugradcalendar.uwaterloo.ca/group/ARTS-Degree-Requirements/?ActiveDate=9/1/"
root = "http://ugradcalendar.uwaterloo.ca/"

url_minor = "https://ugradcalendar.uwaterloo.ca/group/ARTS-Academic-Plans/?ActiveDate=9/1/"

def fetch_degree_req(path, year):
    """
         path: str
         Script to download all html pages for degree req
         return:
    """

    # fetch programs
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    response = http.request('GET', url_plans + str(year))
    data = BeautifulSoup(response.data, 'html.parser')

    majors_links = data.find_all("a", class_="Level2Group")
    for major in majors_links:
        link = root + major["href"] + "/?ActiveDate=9/1/" + str(year)
        if "bachelor" not in major.text.lower() or "bachelor of computing and financial management" in major.text.lower():
            #cfm parsed in math
            continue
        major_reponse = http.request('GET', link)
        major_data = BeautifulSoup(major_reponse.data, 'html.parser')
        major_table = major_data.find_all("a", class_="Level3Group")
        print("Looking for majors/minors in {}...".format(str(major['href'])))
        for l in major_table:
            if "requirements" in str(l.text).lower() and "co-op" not in str(l.text).lower():
                print("Fetching {}...".format(str(l.text)))
                href = root + l['href']
                fileName = href.split("/")[-1]
                a_year = str(year % 1000) + '-' + str(year % 1000 + 1)
                fileName = "/" + a_year + '-' + fileName + ".html"
                resp = get(href)
                with open(path + fileName, 'wb') as fOut:
                    fOut.write(resp.content)


def fetch_faculty_minor(path, year):
    """
             path: str
             Script to download all html pages for Arts Academic Plans
             return:
    """
    pass
    # fetch programs
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    response = http.request('GET', url_minor + str(year))
    data = BeautifulSoup(response.data, 'html.parser')

    program_links = data.find_all("a", class_="Level2Group")
    for program in program_links:
        link = root + program["href"] + "/?ActiveDate=9/1/" + str(year)
        program_reponse = http.request('GET', link)
        program_data = BeautifulSoup(program_reponse.data, 'html.parser')
        program_table = program_data.find_all("a", class_="Level3Group")
        print("Looking for majors/minors in {}...".format(str(program['href'])))
        for l in program_table:
            if "overview" not in str(l.text).lower():
                print("Fetching {}...".format(str(l.text)))
                href = root + l['href'] + "/?ActiveDate=9/1/" + str(year)
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
    #for year in range(cur_year - 5, cur_year + 1):
    for year in range(2019, 2020):
        fetch_degree_req(path, year)
        fetch_faculty_minor(path, year)
