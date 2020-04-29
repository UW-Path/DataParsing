"""
CourseParser.py is a library built to receive information on Major Requirements

Contributors:
Hao Wei Huang
"""

import urllib3
from bs4 import BeautifulSoup
from ProgramParsing.MajorReq import MajorReq
from StringToNumber import StringToNumber
import re
import pkg_resources


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
        major = self.data.find_all("span", id="ctl00_contentMain_lblBottomTitle")

        if major:
            major = major[0].contents[0].string
        else:
            #Exception for Table II data
            return "Table II"
        #Parsing the heading above the highlighted span
        #if major == degree req, spcialization, parse the highlighted span

        if "requirements" in major.lower() or "specializations" in major.lower() or "specialization" in major.lower():
            major = self.data.find_all("span", class_="pageTitle")
            major = str(major[0].contents[0])

        if "Overview and Degree Requirements" in major:
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

    def __getLevelCourses(self, string):
        return re.findall(r"[1-9][0-9][0-9]-", string)

    def require_all(self, list, major, relatedMajor):
        for l in list:
            self.requirement.append(MajorReq([l], "All of", major, relatedMajor, self.additionalRequirement, 0))

    def getAdditionalRequirement(self):
        additionalRequirment = []
        paragraphs = self.data.find_all(["p"]) # cant use span because will get everything else
        for p in paragraphs:
            # a bit hardcoded
            if ("all the requirements" in str(p) or "course requirements" in str(p) or "all requirements" in str(p)) and "plan" in str(p):
                reqs = p.find_all("a")
                print(reqs)
                for req in reqs:
                    # span added for special case for  PMATH additional req #does not work
                    if(not self.__has_numbers(req.contents[0])):
                        additionalRequirment.append(req.contents[0])
        return ", ".join(additionalRequirment)

    def __get_relatedMajor(self, major):
        relatedMajor = self.data.find_all("span", id="ctl00_contentMain_lblTopTitle")
        if relatedMajor:
            relatedMajor = relatedMajor[0].contents[0].string
        else:
            return ""
        if "Academic Plans and Requirements" in relatedMajor:
            return major
        else:
            return relatedMajor

    def __course_list(self, info, i):
        list = []
        while i < len(info):
            line = info[i].strip()
            if line.startswith("Note") and not line.startswith("("):
                i += 1
                continue
            courses = re.findall(r"\b[A-Z]{2,10}\b \b[0-9]{1,4}\b", line)
            if not courses and list:
                # List has ended
                break
            if courses:
                list.append(" or ".join(courses))
            i += 1
        return i, list

    def __additional_list(self, info, i, multiLine):
        list = []
        if multiLine:
            #"Two additional courses from"
            i += 1 #skip first line
            while i < len(info):
                line = info[i].strip()
                foundPattern = False
                if "additional" in line:
                    break #search is over

                # regular CS 135
                courses = re.findall(r"\b[A-Z]{2,10}\b \b[0-9]{1,4}\b", line)
                if courses: foundPattern = True
                for course in courses:
                    list.append(course)

                # range CS 389-CS495
                courses = re.findall(r"[A-Z]+\s{0,1}[1-9][0-9][0-9]\s{0,1}-\s{0,1}[A-Z]+\s{0,1}[1-9][0-9][0-9]",
                                     line)
                if courses:
                    foundPattern = True
                    for course in courses:
                        course = course.strip("\n").strip("\r\n")
                        if not str(course).startswith("("):
                            list.append(course)
                else:
                    # find for another match cs 300-
                    maj = ""
                    match = self.__getLevelCourses(str(line))

                    for word in line.split(' '):
                        if word.isupper() or "math" in word:  # special case for "One additional 300- or 400-level math course.
                            maj = word.strip("\n").strip("\r\n").upper()
                            break
                    if maj.startswith("(") or maj.startswith("Note"):
                        print("No Major Found")
                        #Do nothing
                    elif match:
                        foundPattern =True
                        for m in match:
                            course = m.strip("\n")
                            course = course.strip("\r\n")
                            list.append(maj + " " + course)

                if not foundPattern and list:
                    # List has ended
                    break
                i += 1

        else:
            line = info[i].strip()
            i += 1
            #regular CS 135
            courses = re.findall(r"\b[A-Z]{2,10}\b \b[0-9]{1,4}\b", line)
            for course in courses:
                list.append(course)

            #range CS 389-CS495
            courses = re.findall(r"[A-Z]+\s{0,1}[1-9][0-9][0-9]\s{0,1}-\s{0,1}[A-Z]+\s{0,1}[1-9][0-9][0-9]",line)
            if courses:
                for course in courses:
                    course = course.strip("\n").strip("\r\n")
                    if not str(course).startswith("("):
                        list.append(course)
            else:
                # find for another match cs 300-
                maj = ""
                match = self.__getLevelCourses(str(line))

                for word in line.split(' '):
                    if word.isupper() or "math" in word:  # special case for "One additional 300- or 400-level math course.
                        maj = word.strip("\n").strip("\r\n").upper()
                        break

                if match:
                    for m in match:
                        course = m.strip("\n")
                        course = course.strip("\r\n")
                        list.append(maj + " " + course)
                elif maj:
                    list.append(maj)  # Only indicate major but not level
        return i, list

    def load_file(self, file):
        """
                Parse html file to gather a list of required courses for the major

                :return:
        """
        html = pkg_resources.resource_string(__name__, file)
        # html = open(file, encoding="utf8")
        self.data = BeautifulSoup(html, 'html.parser')

        major = self.__get_major()

        # find the major related to specializations and options
        relatedMajor = self.__get_relatedMajor(major)

        # Find all additional requirement
        self.additionalRequirement = self.getAdditionalRequirement()

        # information = self.data.find_all(['p', 'blockquote'])
        information = self.data.find("span", {'class': 'MainContent'}).get_text().split("\n")


        i = 0
        while i < len(information):
            if "One of" in information[i]:
                i, list = self.__course_list(information, i)
                self.requirement.append(MajorReq(list, "One of", major, relatedMajor, self.additionalRequirement))
            elif "Two of" in information[i]:
                i, list = self.__course_list(information, i)
                self.requirement.append(MajorReq(list, "Two of", major, relatedMajor, self.additionalRequirement))
            elif "Three of" in information[i]:
                i, list = self.__course_list(information, i)
                self.requirement.append(MajorReq(list, "Three of", major, relatedMajor, self.additionalRequirement))
            elif "Four of" in information[i]:
                i, list = self.__course_list(information, i)
                self.requirement.append(MajorReq(list, "Four of", major, relatedMajor, self.additionalRequirement))
            elif "Five of" in information[i]:
                i, list = self.__course_list(information, i)
                self.requirement.append(MajorReq(list, "Five of", major, relatedMajor, self.additionalRequirement))
            elif "Six of" in information[i]:
                i, list = self.__course_list(information, i)
                self.requirement.append(MajorReq(list, "Six of", major, relatedMajor, self.additionalRequirement))
            elif "Seven of" in information[i]:
                i, list = self.__course_list(information, i)
                self.requirement.append(MajorReq(list, "Seven of", major, relatedMajor, self.additionalRequirement))
            elif "Eight of" in information[i]:
                i, list = self.__course_list(information, i)
                self.requirement.append(MajorReq(list, "Eight of", major, relatedMajor, self.additionalRequirement))
            elif "Nine of" in information[i]:
                i, list = self.__course_list(information, i)
                self.requirement.append(MajorReq(list, "Nine of", major, relatedMajor, self.additionalRequirement))
            elif "All of" in information[i]:
                i, list = self.__course_list(information, i)
                self.require_all(list, major, relatedMajor)
            elif "additional" in information[i] and self.__stringIsNumber(information[i]): #should this be and?
                number_additional_string = information[i].lower().split(' ')[0]
                number_additional = StringToNumber[number_additional_string].value
                if not isinstance(number_additional, int):
                    number_additional = number_additional[0]
                #check if one sentence are multiple
                if "." in information[i]:
                    i, list = self.__additional_list(information, i, False)
                else:
                    i, list = self.__additional_list(information, i, True)
                # need to check if number_additional is an INT
                self.requirement.append(MajorReq(list, "Additional", major, relatedMajor, self.additionalRequirement, number_additional))
            else:
                i += 1

    def __str__(self):
        output = ""
        for req in self.requirement:
            output += str(req) + "\n"
        return output

