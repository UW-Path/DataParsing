"""
CourseParser.py is a library built to receive information on Major Requirements

Contributors:
Hao Wei Huang
Calder Lund
"""

from bs4 import BeautifulSoup
from ProgramParsing.Science.MajorReq import ScienceMajorReq
from ProgramParsing.ProgramParser.MajorParser import MajorParser
import re
import pkg_resources
from math import ceil


class ScienceMajorParser(MajorParser):
    def _get_program(self):
        program = self.data.find_all("span", id="ctl00_contentMain_lblBottomTitle")

        if program:
            program = program[0].contents[0].string

        #check for minor
        minor = self.data.find_all("span", class_="pageTitle")
        minor = str(minor[0].contents[0])

        if "minor" in str(minor).lower():
            program = minor

        return program
        # TODO: Need a case where this tile area is Degree Requirements

    def _course_list(self, line, credit, oneOf = False):
        list = []
        line = line.strip().replace(" to ", "-")

        d = dict() #dictionary to keep track of courses

        if line.startswith("Note") or line.startswith("("):
            return []


        rangeCourse = re.findall(r"[A-Z]+\s{0,1}[1-9][0-9][0-9]\s{0,1}-\s{0,1}[A-Z]+\s{0,1}[1-9][0-9][0-9]",
                             line)
        courses = re.findall(r"\b[A-Z]{2,10}\b \b[0-9]{1,4}[A-Z]{0,1}\b", line)

        orCourse = re.findall(r"\b[A-Z]{2,10}\b \b[0-9]{1,4}[A-Z]{0,1}\b or \b[A-Z]{2,10}\b \b[0-9]{1,4}[A-Z]{0,1}\b", line)

        if orCourse:
            # CS 135 or CS XXX
            for oC in orCourse:
                c = oC.split(" or ")
                d[c[0]] = True
                d[c[1]] = True
                list.append(oC)

        if rangeCourse:
            #TODO: Account for range CS 123-CS 345, excluding CS XXX
            if oneOf:
                for c in rangeCourse:
                    list.append(c)
            else: list.append(" or ".join(rangeCourse))

        if courses:
            for c in courses:
                if c not in d:
                    list.append(c)

        if not list:
            r = self._getLevelCourses(line)
            if r:
                #assume only 200- for now
                maj = ""
                for word in line.split(' '):
                    if word.isupper():
                        maj = word.strip("\n").strip("\r\n").upper()
                        break
                list.append(maj + " " + r[0])
                if len(r) > 1:
                    print("ERROR more than one match 200- found")

        if list:
            c = self._count_credits(list)
            if credit == c or len(list) == 1:
                #Note: 1 is coded as a special case. Not perfect accuracy in terms of credit count
                return list, True

        return list, False

    def _count_credits(self,list):
        count = 0
        for course in list:
            courseNum = course.split(" ")[1]
            if "L" in courseNum:
                count += 0.25
            else:
                count += 0.5
        return float(count)

    def _require_all(self, list, major, relatedMajor, additionalRequirement):
        #TODO: Match with database credits
        #TODO: Dafault as 0.5 credits
        for course in list:
            self.requirement.append(ScienceMajorReq([course], 1, major, relatedMajor, additionalRequirement, 0.5))

    def load_file(self, file):
        """
                Parse html file to gather a list of required courses for the major

                :return:
        """
        html = pkg_resources.resource_string(__name__, file)
        # html = open(file, encoding="utf8")
        self.data = BeautifulSoup(html, 'html.parser')

        program = self._get_program()

        # find the major related to specializations and options
        relatedMajor = self._get_relatedMajor(program)

        # Find all additional requirement
        self.additionalRequirement = self.getAdditionalRequirement()

        information = self.data.find("span", {'class': 'MainContent'}).get_text().split("\n")

        i = 0
        while i < len(information):
            line = information[i]
            credits = line.split(' ')[0]
            try:
                credits = float(credits)
                numCourse = ceil(credits / 0.5)

            except:
                i+=1
                continue

            try:
                list, insertAll = self._course_list(line, credits)
                if list:
                    if insertAll:
                        self._require_all(list, program, relatedMajor, self.additionalRequirement)
                    else:
                        self.requirement.append(ScienceMajorReq(list, numCourse, program, relatedMajor, self.additionalRequirement, credits))
                elif "elective" in line.split(' ')[1]:
                    list.append("Elective")
                    self.requirement.append(ScienceMajorReq(list, numCourse, program, relatedMajor, self.additionalRequirement, credits))

            except (RuntimeError):
                print(RuntimeError)
                pass
                #not parsable
            i += 1


