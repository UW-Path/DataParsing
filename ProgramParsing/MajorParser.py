"""
CourseParser.py is a library built to receive information on Major Requirements

Date:
October 14th, 2019

Updated:
October 19th, 2019

Contributors:
Hao Wei Huang
"""

import urllib3
from bs4 import BeautifulSoup


class MajorParser:
    def __init__(self):
        self.http = urllib3.PoolManager()
        self.data = None
        self.requirement = []

    def load_url(self, url):
        response = self.http.request('GET', url)
        self.data = BeautifulSoup(response.data, 'html.parser')

    def is_blockquote(self, html):
        i = html.find("a")
        if i:
            return True
        else:
            return False

    def require_all(self, html):
        courses = html.findAll("a")
        for course in courses:
            self.requirement.append(course.contents[0])

    def require_one(self, html):
        list = []
        courses = html.findAll("a")
        for course in courses:
            list.append(course.contents[0])
        self.requirement.append(", ".join(list))

    def load_file(self, file):
        html = open(file)
        self.data = BeautifulSoup(html, 'html.parser')
        information = self.data.find_all(['p','blockquote'])

        i = 0
        while i < len(information):
            # check if next var is blockquote
            if i + 1 < len(information) and self.is_blockquote(information[i+1]):
                if "One of" in str(information[i]):
                    self.require_one(information[i + 1])
                elif "All of" in str(information[i]):
                    self.require_all(information[i+1])
                i += 1
            # TODO: All the other special cases that requires additional parsing
            i += 1


if __name__ == "__main__":
    file = "RequiredCSMajor.html"

    parser = MajorParser()
    parser.load_file(file)

    print(parser.requirement)
