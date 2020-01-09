"""
Parses information about which communication courses must be taken in a degree's requirements.

Contributors:
Calder Lund
"""

import re

import pkg_resources
from bs4 import BeautifulSoup


class Communications:
    def __init__(self):
        self.__list1 = []
        self.__list2 = []

    def load_file(self, file):
        html = pkg_resources.resource_string(__name__, file)
        ### Below doesn't work for all
        # html = open(file, encoding="ISO-8859-1")
        self.data = BeautifulSoup(html, 'html.parser')
        ul = self.data.find_all("ul")
        list_num = 0

        for u in ul:
            courses = u.find_all("a", href=re.compile("courses"))
            if len(courses):
                list_num += 1
            for course in courses:
                if list_num == 1:
                    self.__list1.append(course.text)
                if list_num == 2:
                    self.__list2.append(course.text)

    def is_in_list1(self, course_code):
        return course_code in self.__list1

    def is_in_list2(self, course_code):
        return course_code in self.__list2 or self.is_in_list1(course_code)

    def get_list1(self):
        return self.__list1

    def get_list2(self):
        return self.__list2

    def __str__(self):
        output = "List 1:\n"
        for course in self.__list1:
            output += "- " + course + "\n"

        output += "List 2:\n"
        for course in self.__list2:
            output += "- " + course + "\n"
        return output
