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
import re


class MajorParser:
    def __init__(self):
        self.http = urllib3.PoolManager()
        self.data = None
        self.requirement = []
        self.additionalRequirement = ""

    def load_url(self, url):
        response = self.http.request('GET', url)
        self.data = BeautifulSoup(response.data, 'html.parser')

    def __has_numbers(self, input_string):
        """
                Check if input_string has numbers (0-9)
                :return: bool
        """
        return bool(re.search(r'\d', input_string))

    def __get_major(self):
        major = self.data.find_all("span", id= "ctl00_contentMain_lblBottomTitle")
        major = major[0].contents[0].string

        #Parsing the heading above the highlighted span
        #if major == degree req, spcialization, parse the highlighted span

        if ("requirements" in major.lower() or "specializations" in major.lower()):
            major = self.data.find_all("span", class_="pageTitle")
            major = str(major[0].contents[0])

        if ("Overview and Degree Requirements" in major):
            major = major.replace(" Overview and Degree Requirements", "")

        return major
        # TODO: Need a case where this tile area is Degree Requirements

    def __stringIsNumber(self, s):
        s = str(s).split(" ")[0].lower()
        if "one" in s or "one" in s or "two" in s or "three" in s or "four" in s or "five" in s \
                or "six" in s or "seven" in s or "eight" in s or "nine" in s or "ten" in s:
            return True
        else:
            return False

    def is_blockquote(self, html):
        return html.name == "blockquote"

    def require_all(self, html, major):
        courses = html.findAll("a")
        for course in courses:
            #TODO: need to accept ENGL378/MATH111 format (right now only takes in ENGL378)
            self.requirement.append(MajorReq(course, "All of", major, self.additionalRequirement))

    def getAdditionalRequirement(self):
        additionalRequirment = []
        paragraphs = self.data.find_all(["p"]) #cant use span because will get everything else
        for p in paragraphs:
            #a bit hardcoded
            if (("all the requirements" in str(p) or "course requirements" in str(p) or "all requirements" in str(p)) and "plan" in str(p)):
                reqs = p.find_all("a")
                print(reqs)
                for req in reqs:
                    #span added for special case for  PMATH additional req #does not work
                    if(not self.__has_numbers(req.contents[0])):
                        additionalRequirment.append(req.contents[0])
        return ", ".join(additionalRequirment)
    def load_file(self, file):
        """
                Parse html file to gather a list of required courses for the major

                :return:
        """
        html = open(file, encoding="utf8")
        self.data = BeautifulSoup(html, 'html.parser')


        major = self.__get_major()

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
                else:
                    i += 1
                i += 1
            elif "additional" in str(information[i]) or self.__stringIsNumber(str(information[i])):
                if (i == 0): #special case first p cannot be additional
                    i += 1
                    continue
                #make sure there's a tag and format such as "Three 400- level courses (without additional)
                if (information[i].contents[0].name == None) and not (self.__stringIsNumber(str(information[i]))):
                    i += 1
                    continue

                number_additional_string = str(information[i].contents[0]).lower().split(' ')[0]

                number_additional = StringToNumber[number_additional_string].value
                if (not isinstance(number_additional, int)):
                    number_additional = number_additional[0]
                #need to check if number_additional is an INT
                self.requirement.append(MajorReq(information[i], "Additional", major, self.additionalRequirement, number_additional))

            # TODO: All the other special cases that requires additional parsing
            i += 1

    def __str__(self):
        output = ""
        for req in self.requirement:
            output += str(req) + "\n"
        return output

