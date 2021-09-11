"""
The purpose of this script is to update the HTML of Degree Requirement for a calender year

Contributors:
Hao Wei Huang
"""

import os
import urllib3
from bs4 import BeautifulSoup
from requests import get
from ProgramParsing.ProgramParser.ENV_VARIABLES.PARSE_YEAR import PARSE_YEAR_BEG, PARSE_YEAR_END

# pre 2019
url_plans1 = "https://ugradcalendar.uwaterloo.ca/group/SCI-Science-Academic-Plans/?ActiveDate=9/1/"
# post 2019
url_plans2 = "https://ugradcalendar.uwaterloo.ca/group/SCI-Science-Academic-Programs-and-Plans1/?ActiveDate=9/1/"

root = "http://ugradcalendar.uwaterloo.ca/"
url_minor = "https://ugradcalendar.uwaterloo.ca/group/SCI-Minors-Options-Joint-Progs-Internat-Partner/?ActiveDate=9/1/"


def fetch_degree_req(path, year):
    """
         path: str
         Script to download all html pages for degree req
         return:
    """

    link_to_ignore = ["List of Plans and Common Degree Requirements",
                      "Pharmacy", "Optometry"]

    if year < 2019:
        url_plans = url_plans1
    else:
        url_plans = url_plans2

    #fetch programs
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    response = http.request('GET', url_plans + str(year))
    data = BeautifulSoup(response.data, 'html.parser')

    majors_links = data.find_all("a", class_="Level2Group")
    for major in majors_links:
        link = root + major["href"] + '/?ActiveDate=9/1/' + str(year)
        if major.text in link_to_ignore:
            continue
        major_reponse = http.request('GET', link)
        major_data = BeautifulSoup(major_reponse.data, 'html.parser')
        major_table = major_data.find_all("a", class_="Level3Group")
        print("Looking for minors in {}...".format(str(major['href'])))
        for l in major_table:
            #exceptions to programs that only offer coop programs
            exception = ["Biotechnology/Economics", "Medicinal Chemistry", "Biotechnology/Chartered Professional Accountancy", "Science and Business"]
            if "co-operative" in str(l.text).lower() or "overview" in str(l.text).lower():
                isExcep = False
                for e in exception:
                    if e.lower() in str(l.text).lower():
                        isExcep = True
                        break
                if not isExcep:
                    continue
            if ("overview" in str(l.text).lower()
                    or "recommended course" in str(l.text).lower()
                    or "important info" in str(l.text).lower()):
                continue

            print("Fetching {}...".format(str(l.text)))
            href = root + l['href'] + '/?ActiveDate=9/1/' + str(year)
            fileName = href.split("/")[-4]
            a_year = str(year) + '-' + str(year + 1)
            fileName = "/" + a_year + '-' + fileName + ".html"
            resp = get(href)
            with open(path + fileName, 'wb') as fOut:
                fOut.write(resp.content)

def fetch_faculty_minor(path, year):
    """
             path: str
             Script to download all html pages for minors in Faculty of Math
             return:
    """
    link_to_ignore = ["Academic Plans and Requirements", "Degree Requirements for all Math students"]

    # fetch programs
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    response = http.request('GET', url_minor + str(year))
    data = BeautifulSoup(response.data, 'html.parser')

    table = data.find_all("a", class_="Level3Group")

    for minor in table:
        if str(minor.text) not in link_to_ignore:
            print("Fetching {}...".format(str(minor.text)))
            href = root + minor['href'] + '/?ActiveDate=9/1/' + str(year)
            fileName = href.split("/")[-4]
            a_year = str(year) + '-' + str(year + 1)
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

    for year in range(PARSE_YEAR_BEG, PARSE_YEAR_END + 1):
        fetch_degree_req(path, year)
        # pre 2019 is pulled in with fetch_degree_req
        if year >= 2019:
            fetch_faculty_minor(path, year)
