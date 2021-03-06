"""
The purpose of this script is to update the HTML of Degree Requirement for a calender year
"""

import os
import urllib3
from bs4 import BeautifulSoup
from requests import get


plans = ["https://ugradcalendar.uwaterloo.ca/group/AHS-Department-of-Kinesiology",
         "https://ugradcalendar.uwaterloo.ca/group/AHS-Department-of-Recreation-and-Leisure-Studies",
         "https://ugradcalendar.uwaterloo.ca/group/AHS-School-of-Public-Health-and-Health-Systems"]

root = "http://ugradcalendar.uwaterloo.ca/"

def fetch_degree_req(path):
    """
         path: str
         Script to download all html pages for degree req
         return:
    """
    link_to_ignore = ["Overview", "Joint Honours Degree", "Joint Honours Degrees", "Minors", "Accelerated Master's Program",
                      "Gerontology", "The Area of Gerontology"]

    # fetch programs
    http = urllib3.PoolManager()
    for plan in plans:
        response = http.request('GET', plan)
        data = BeautifulSoup(response.data, 'html.parser')

        tables = [data.find_all("a", class_="Level2Group"),  data.find_all("a", class_="Level3Group")]

        for table in tables:
            for program in table:
                prog_text = str(program.text)
                if prog_text not in link_to_ignore:
                    print("Fetching {}...".format(prog_text))
                    href = root + program['href']
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
