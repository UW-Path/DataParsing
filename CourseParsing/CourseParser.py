"""
CourseParser.py is a library built to receive information on courses and
their respected prerequisites.

Contributors:
Calder Lund
"""

import urllib3
from bs4 import BeautifulSoup
from CourseParsing.Course import Course
import pkg_resources

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

    def load_html(self, html):
        self.data = BeautifulSoup(html, 'html.parser')
        information = self.data.find_all("center")
        for info in information:
            self.courses.append(Course(info))

    def load_file(self, file):
        html = pkg_resources.resource_string(__name__, file)
        # html = open(file, encoding="ISO-8859-1")
        self.load_html(html)

    def __str__(self):
        output = ""
        for course in self.courses:
            output += str(course) + "\n"
        return output
