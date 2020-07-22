"""
CourseParser.py is a library built to receive information on Major Requirements

Contributors:
Hao Wei Huang
"""

from bs4 import BeautifulSoup
from ProgramParsing.Environment.MajorReq import EnvironmentMajorReq
from ProgramParsing.ProgramParser.MajorParser import MajorParser
import re
import pkg_resources
from math import ceil
from Database.DatabaseReceiver import DatabaseReceiver
from StringToNumber import StringToNumber


class EnvironmentMajorParser(MajorParser):
    def _get_program(self):
        program = self.data.find_all("span", id="ctl00_contentMain_lblPageTitle")
        # didn't account for minor
        if program:
            #Honours Biochemistry, Biotechnology Specialization format then take second
            program = program[0].contents[0].string
            if ", " in program:
                program = program.split(", ")[1]
            #special for env
            program = program.replace("Requirements", "")
            program= program.lstrip().rstrip()

        return program
        # TODO: Need a case where this tile area is Degree Requirements

    def _course_list(self, line, oneOf = False):
        list = []
        if "elective" in line:
            return ["Elective"]
        if "breadth requirement" in line.lower():
            return ["Breadth Requirement"]

        d = dict() #dictionary to keep track of courses

        if line.startswith("Note") or line.startswith("("):
            return []


        rangeCourse = re.findall(r"[A-Z]+\s{0,1}[1-9][0-9][0-9]\s{0,1}-\s{0,1}[A-Z]+\s{0,1}[1-9][0-9][0-9]",
                             line)
        courses = re.findall(r"\b[A-Z]{2,10}\b \b[0-9]{1,4}[A-Z]{0,1}", line)

        orCourse = re.findall(r"\b(?<!\/)[A-Z]{2,10}\b \b[0-9]{1,4}[A-Z]{0,1}\b or \b[A-Z]{2,10}\b \b[0-9]{1,4}[A-Z]{0,1}\b", line)

        if orCourse:
            # CS 135 or CS XXX
            for oC in orCourse:
                c = oC.split(" or ")
                d[c[0]] = True
                d[c[1]] = True
                list.append(", ".join(c))

        if rangeCourse:
            #TODO: Account for range CS 123-CS 345, excluding CS XXX
            # if oneOf:
            for c in rangeCourse:
                list.append(c)
            # else: list.append(" or ".join(rangeCourse))

        if courses:
            for c in courses:
                if c not in d:
                    list.append(c)

        if not list:
            maj = ""

            majors = []
            for word in line.split(' '):
                if word.isupper():
                    temp = word.replace(",", "")
                    if temp not in majors:
                        majors.append(temp)

            maj = ", ".join(majors)
            if maj:
                list.append(maj)

        if not list:
            if "Elective" in line:
                return ["Elective"]
            return []

        return list

    def _count_credits(self,list):
        dbc = DatabaseReceiver()
        count = 0
        for course in list:
            course = course.split(", ")[0] #or course like cs135, cs136 in course

            try:
                count += float(dbc.select_course_credit(course))
            except:
                print(course)
                count += 0.5

        dbc.close()
        return float(count)

    def _require_all(self, list, major, relatedMajor, additionalRequirement):
        #TODO: Match with database credits
        #TODO: Dafault as 0.5 credits
        for course in list:
            self.requirement.append(EnvironmentMajorReq([course], 1, major, relatedMajor, additionalRequirement, 0.5))


    def get_text(self, td):
        #filter out subscript
        INVALID_TAGS = ['sup']

        for tag in td.findAll(True):
            if tag.name in INVALID_TAGS:
                tag.replaceWith("")
        return td.text


    def load_file(self, file):
        """
                Parse html file to gather a list of required courses for the major

                :return:
        """
        html = pkg_resources.resource_string(__name__, file)
        # html = open(file, encoding="utf8")
        self.data = BeautifulSoup(html, 'html.parser')

        program = self._get_program()

        # Engineering only has majors
        relatedMajor = program

        #check if it has a table format

        information = self.data.find("span", {'class': 'MainContent'})




        i = 0
        information = information.text.split("\n")
        term = ""
        #terminate after 4B is ran

        while i < len(information):
            line = str(information[i]).lstrip().rstrip()
            if line == "Notes":
                #end of file
                break
            #initialize term

            isTerm = re.findall(r"Year (One|Two|Three|Four)", line)
            if isTerm:
                term = isTerm[0]
                if "One" in term:
                    term = "1"
                elif "Two" in term:
                    term = "2"
                elif "Three" in term:
                    term = "3"
                elif "Four" in term:
                    term = "4"
            elif term != "":
                number_additional = 1
                try:
                    number_additional_string = line.split(' ')[0].lower()
                    number_additional = StringToNumber[number_additional_string].value
                    if not isinstance(number_additional, int):
                        number_additional = number_additional[0]
                except:
                    #not a number
                    pass

                list = self._course_list(line)
                if list:
                    credits = self._count_credits(list) / len(list) * number_additional
                    self.requirement.append(
                        EnvironmentMajorReq(list, number_additional, program, relatedMajor, term, credits))



            i += 1


