"""
CourseParser.py is a library built to receive information on courses and
their respected prerequisites.

Date:
October 10th, 2019

Contributors:
Calder Lund
"""

import urllib3
from bs4 import BeautifulSoup
from Course import Course
from Database import *

class CourseParser:
    '''
    TODO - Document this portion of code
    CourseParser()
    '''

    def __init__(self):
        self.http = urllib3.PoolManager()
        self.data = None
        self.courses = []

    def load_url(self, url):
        response = self.http.request('GET', url)
        self.data = BeautifulSoup(response.data, 'html.parser')

    def load_file(self, file):
        html = open(file)
        self.data = BeautifulSoup(html, 'html.parser')
        info = self.data.find_all("center")
        for i in info:
            self.courses.append(Course(i))

    def __str__(self):
        output = ""
        for course in self.courses:
            output += str(course) + "\n"
        return output

if __name__ == "__main__":
    file = "CoursesCS1920.html"

    parser = CourseParser()
    parser.load_file(file)
    print(parser)

    insert_courses(parser.courses)
