'''
CourseParser.py is a library built to receive information on courses
and their respected prerequisites.

Date:
October 10th, 2019

Contributors:
Calder Lund
'''

import urllib3
from bs4 import BeautifulSoup
from Course import Course

class CourseParser():
    '''
    CourseParser()
    '''

    def __init__(self):
        self.http = urllib3.PoolManager()
        self.data = None

    def load_url(self, url):
        response = self.http.request('GET', url)
        self.data = BeautifulSoup(response.data, 'html.parser')

    def load_file(self, file):
        html = open(file)
        self.data = BeautifulSoup(html, 'html.parser')

    '''def get_courses(self):
        courses = []
        all = self.data.find_all('a')
        for course in all:
            code = course.get("name")
            if code and not code.endswith("S"):
                courses.append(course.get("name"))
        return courses
    '''
    def get_courses(self):
        courses = []
        for c in self.info:
            c.find_all("a")

    def get_prereqs(self):
        prereqs = []
        all = self.data.find_all("i")
        for a in all:
            if a and a.string \
               and a.string.startswith("Prereq:"):
                prereqs.append(a.string)
        return prereqs

    def get_course_info(self):
        self.info = self.data.find_all("center")
        self.courses = []
        for info in self.info:
            Course(info)



    def __str__(self):
        all = self.data.find_all("i")
        return str(all)
        

if __name__ == "__main__":
    file = "CoursesCS1920.html"

    parser = CourseParser()
    parser.load_file(file)

    parser.get_course_info()