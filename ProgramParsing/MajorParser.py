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
        self.additionalRequirement = ""

    def load_url(self, url):
        response = self.http.request('GET', url)
        self.data = BeautifulSoup(response.data, 'html.parser')

    def is_blockquote(self, html):
        return html.name == "blockquote"

    def require_all(self, html, major):
        courses = html.findAll("a")
        for course in courses:
            #TODO: need to accept ENGL378/MATH111 format (right now only takes in ENGL378)
            self.requirement.append(MajorReq(course, "All of", major, self.additionalRequirement))

    def getAdditionalRequirement(self):
        additionalRequirment = []
        paragraphs = self.data.find_all("p")
        for p in paragraphs:
            #a bit hardcoded
            if ("all the requirements" in str(p) and "plan" in str(p)):
                reqs = p.find_all("a")
                print(reqs)
                for req in reqs:
                    additionalRequirment.append(req.contents[0])
        return ", ".join(additionalRequirment)
    def load_file(self, file):
        """
                Parse html file to gather a list of required courses for the major

                :return:
        """
        html = open(file, encoding="utf8")
        self.data = BeautifulSoup(html, 'html.parser')

        major = self.data.find_all("span", class_="pageTitle")
        major = str(major[0].contents[0])

        if ("Overview and Degree Requirements" in major):
            major = major.replace(" Overview and Degree Requirements", "")

        #Find all additional requirement
        self.additionalRequirement = self.getAdditionalRequirement()


        information = self.data.find_all(['p', 'blockquote'])

        i = 0
        while i < len(information):
            # check if next var is blockquote
            if i + 1 < len(information) and self.is_blockquote(information[i+1]):
                if "One of" in str(information[i]):
                    self.requirement.append(MajorReq(information[i + 1], "One of", major, self.additionalRequirement))
                elif "Two of" in str(information[i]):
                    self.requirement.append(MajorReq(information[i + 1], "Two of", major, self.additionalRequirement))
                elif "Three of" in str(information[i]):
                    self.requirement.append(MajorReq(information[i + 1], "Three of", major, self.additionalRequirement))
                elif "Four of" in str(information[i]):
                    self.requirement.append(MajorReq(information[i + 1], "Four of", major, self.additionalRequirement))
                elif "Five of" in str(information[i]):
                    self.requirement.append(MajorReq(information[i + 1], "Five of", major, self.additionalRequirement))
                elif "Six of" in str(information[i]):
                    self.requirement.append(MajorReq(information[i + 1], "Six of", major, self.additionalRequirement))
                elif "Seven of" in str(information[i]):
                    self.requirement.append(MajorReq(information[i + 1], "Seven of", major, self.additionalRequirement))
                elif "Eight of" in str(information[i]):
                    self.requirement.append(MajorReq(information[i + 1], "Eight of", major, self.additionalRequirement))
                elif "Nine of" in str(information[i]):
                    self.requirement.append(MajorReq(information[i + 1], "Nine of", major, self.additionalRequirement))
                elif "All of" in str(information[i]):
                    self.require_all(information[i+1], major)
                elif "additional" in str(information[i]):
                    number_additional_string = str(information[i].contents[0]).lower().split(' ')[0]
                    number_additional = StringToNumber[number_additional_string].value[0]
                    self.requirement.append(MajorReq(information[i + 1], "Additional", major, self.additionalRequirement, number_additional))
                i += 1
            elif "additional" in str(information[i]):
                if (i == 0): #special case first p cannot be additional
                    i += 1
                    continue
                if (information[i].contents[0].name == None):
                    i += 1
                    continue

                number_additional_string = str(information[i].contents[0]).lower().split(' ')[0]

                number_additional = StringToNumber[number_additional_string].value[0]
                self.requirement.append(MajorReq(information[i], "Additional", major, self.additionalRequirement, number_additional))

            # TODO: All the other special cases that requires additional parsing
            i += 1

    def __str__(self):
        output = ""
        for req in self.requirement:
            output += str(req) + "\n"
        return output

