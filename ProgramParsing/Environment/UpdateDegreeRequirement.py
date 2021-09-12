"""
The purpose of this script is to update the HTML of Degree Requirement for a calender year
"""

import os
import urllib3
from bs4 import BeautifulSoup
from requests import get
from ProgramParsing.ProgramParser.ENV_VARIABLES.PARSE_YEAR import PARSE_YEAR_BEG, PARSE_YEAR_END


plans_2021_newer = ["https://ugradcalendar.uwaterloo.ca/group/ENV-Environment-Academic-Plans"]

plans_2020_older = ["https://ugradcalendar.uwaterloo.ca/group/ENV-Environment-Enterprise-and-Development",
                    "https://ugradcalendar.uwaterloo.ca/group/ENV-Department-of-Knowledge-Integration",
                    "https://ugradcalendar.uwaterloo.ca/group/ENV-School-Environment-Resources-Sustainability",
                    "https://ugradcalendar.uwaterloo.ca/group/ENV-Department-of-Geography-and-Environmental-Mgmt",
                    "https://ugradcalendar.uwaterloo.ca/group/ENV-School-of-Planning"]

#for now we are only parsing the plans
pages = ["https://ugradcalendar.uwaterloo.ca/page/ENV-Honours-Co-operative-Planning",
         "https://ugradcalendar.uwaterloo.ca/page/ENV-Env-Res-Sus-Env-Res-Stud-Hons-Reg-Co-op",
         "https://ugradcalendar.uwaterloo.ca/page/ENV-Bachelor-of-Knowledge-Integration-1",
         "https://ugradcalendar.uwaterloo.ca/page/ENV-Honours-Environment-Business-Co-op-and-Reg",
         "https://ugradcalendar.uwaterloo.ca/page/ENV-Honours-International-Development",
         "https://ugradcalendar.uwaterloo.ca/page/ENV-Geography-Environmental-Management-3-Yr-Gen",
         "https://ugradcalendar.uwaterloo.ca/page/ENV-Geography-Environmental-Management-4-Yr-Honour",
         "https://ugradcalendar.uwaterloo.ca/page/ENV-Honours-Geography-and-Aviation-Regular",
         "https://ugradcalendar.uwaterloo.ca/page/ENV-Honours-Geomatics-Regular-and-Co-op"]

root = "http://ugradcalendar.uwaterloo.ca/"

def fetch_plan(path, year):
    """
         path: str
         Script to download all html pages for degree req
         return:
    """
    link_to_ignore = ["Overview", "Accelerated Master's"]
    # uses the correct set of plans depending on the year
    if year >= 2021:
        plans = plans_2021_newer
    else:
        plans = plans_2020_older

    # fetch programs
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    for plan in plans:
        response = http.request('GET', plan + "/?ActiveDate=9/1/" + str(year))
        data = BeautifulSoup(response.data, 'html.parser')

        subpages = data.find_all("a", class_="Level2Group")

        for subpage in subpages:
            group_link = root + subpage['href']
            response = http.request('GET', group_link)
            data = BeautifulSoup(response.data, 'html.parser')
            table = data.find_all("a", class_="Level3Group")

            for program in table:
                prog_text = str(program.text)
                if "diploma" in prog_text.lower():
                    continue
                if prog_text not in link_to_ignore:
                    print("Fetching {}...".format(prog_text))
                    href = root + program['href'] + '/?ActiveDate=9/1/' + str(year)
                    fileName = href.split("/")[-4]
                    # undergrad calendar year
                    a_year = str(year) + '-' + str(year + 1)
                    fileName = "/" + a_year + '-' + fileName + ".html"
                    resp = get(href)
                    with open(path + fileName, 'wb') as fOut:
                        fOut.write(resp.content)

def fetch_pages(path, year):
    for href in pages:
        fileName = href.split("/")[-1]
        print("Fetching {}...".format(fileName))
        # undergrad calendar year
        a_year = str(year) + '-' + str(year + 1)
        fileName = "/" + a_year + '-' + fileName + ".html"
        href = href + "/?ActiveDate=9/1/" + str(year)
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
        if year >= 2021:
            fetch_plan(path, year)
        else:
            fetch_pages(path, year)

