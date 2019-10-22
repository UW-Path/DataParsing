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
from ProgramParsing.MajorReq import MajorReq
from StringToNumber import StringToNumber


class MajorParser:
    def __init__(self):
        self.http = urllib3.PoolManager()
        self.data = None
        self.requirement = []

    def load_url(self, url):
        response = self.http.request('GET', url)
        self.data = BeautifulSoup(response.data, 'html.parser')

    def is_blockquote(self, html):
        return html.name == "blockquote"

    def require_all(self, html, major):
        courses = html.findAll("a")
        for course in courses:
            #TODO: need to accept ENGL378/MATH111 format (right now only takes in ENGL378)
            self.requirement.append(MajorReq(course, "All of", major))

    def load_file(self, file):
        """
                Parse html file to gather a list of required courses for the major

                :return:
        """
        html = open(file)
        self.data = BeautifulSoup(html, 'html.parser')

        major = self.data.find_all("span", class_="pageTitle")
        major = str(major[0].contents[0])

        if ("Overview and Degree Requirements" in major):
            major = major.replace(" Overview and Degree Requirements", "")

        information = self.data.find_all(['p', 'blockquote'])

        i = 0
        while i < len(information):
            if (i == 28):
                print("HI")
            # check if next var is blockquote
            if i + 1 < len(information) and self.is_blockquote(information[i+1]):
                if "One of" in str(information[i]):
                    self.requirement.append(MajorReq(information[i + 1], "One of", major))
                elif "Two of" in str(information[i]):
                    self.requirement.append(MajorReq(information[i + 1], "Two of", major))
                elif "Three of" in str(information[i]):
                    self.requirement.append(MajorReq(information[i + 1], "Three of", major))
                elif "All of" in str(information[i]):
                    self.require_all(information[i+1], major)
                elif "additional" in str(information[i]):
                    number_additional_string = str(information[i].contents[0]).lower().split(' ')[0]
                    number_additional = StringToNumber[number_additional_string].value[0]
                    self.requirement.append(MajorReq(information[i + 1], "Additional", major, number_additional))
                i += 1
            elif "additional" in str(information[i]):
                number_additional_string = str(information[i].contents[0]).lower().split(' ')[0]
                number_additional = StringToNumber[number_additional_string].value[0]
                self.requirement.append(MajorReq(information[i], "Additional", major, number_additional))

            # TODO: All the other special cases that requires additional parsing
            i += 1

    def __str__(self):
        output = ""
        for req in self.requirement:
            output += str(req) + "\n"
        return output

