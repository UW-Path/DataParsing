"""
The purpose of this script is to update the HTML of Degree Requirement for a calender year
"""

import os
import urllib3
from bs4 import BeautifulSoup
from requests import get
from ProgramParsing.ProgramParser.ENV_VARIABLES.PARSE_YEAR import PARSE_YEAR_BEG, PARSE_YEAR_END

# pre 2021-2022
plans_old = ["https://ugradcalendar.uwaterloo.ca/group/AHS-Department-of-Kinesiology/?ActiveDate=9/1/",
         "https://ugradcalendar.uwaterloo.ca/group/AHS-Department-of-Recreation-and-Leisure-Studies/?ActiveDate=9/1/",
         "https://ugradcalendar.uwaterloo.ca/group/AHS-School-of-Public-Health-and-Health-Systems/?ActiveDate=9/1/"]

# 2021-2022 onwards
plans_new = ["https://ugradcalendar.uwaterloo.ca/group/HEA-Department-of-Kinesiology/?ActiveDate=9/1/",
             "https://ugradcalendar.uwaterloo.ca/group/HEA-Department-of-Recreation-and-Leisure-Studies/?ActiveDate=9/1/",
             "https://ugradcalendar.uwaterloo.ca/group/HEA-School-of-Public-Health-and-Health-Systems/?ActiveDate=9/1/"]

root = "http://ugradcalendar.uwaterloo.ca/"

def fetch_degree_req(path, year):
    """
         path: str
         Script to download all html pages for degree req
         return:
    """
    link_to_ignore = ["Overview", "Joint Honours Degree", "Joint Honours Degrees", "Minors", "Accelerated Master's Program",
                      "Gerontology", "The Area of Gerontology"]

    if year >= 2021:
        plans = plans_new
    else:
        plans = plans_old

    # fetch programs
    http = urllib3.PoolManager(cert_reqs='CERT_NONE')
    for plan in plans:
        response = http.request('GET', plan + str(year))
        data = BeautifulSoup(response.data, 'html.parser')

        tables = [data.find_all("a", class_="Level2Group"),  data.find_all("a", class_="Level3Group")]

        for table in tables:
            for program in table:
                prog_text = str(program.text)
                if prog_text not in link_to_ignore:
                    print("Fetching {}...".format(prog_text))
                    href = root + program['href'] + '/?ActiveDate=9/1/' + str(year)
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
