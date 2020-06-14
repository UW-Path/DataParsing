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

    pass

def fetch_faculty_minor(path):
    """
             path: str
             Script to download all html pages for minors in Faculty of Math
             return:
    """
    pass


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
