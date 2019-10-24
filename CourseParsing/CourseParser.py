"""
CourseParser.py is a library built to receive information on courses and
their respected prerequisites.

Date:
October 10th, 2019

Updated:
October 19th, 2019

Contributors:
Calder Lund
"""

import urllib3
from bs4 import BeautifulSoup
from CourseParsing.Course import Course


class CourseParser:
    """
    TODO - Document this portion of code
    CourseParser()
    """

    def __init__(self):
        self.http = urllib3.PoolManager()
        self.data = None
        self.courses = []

    def load_url(self, url):
        response = self.http.request('GET', url)
        self.data = BeautifulSoup(response.data, 'html.parser')

    def load_file(self, file):
        html = open(file, encoding="utf8")
        self.data = BeautifulSoup(html, 'html.parser')
        information = self.data.find_all("center")
        for info in information:
            self.courses.append(Course(info))

    def __str__(self):
        output = ""
        for course in self.courses:
            output += str(course) + "\n"
        return output
