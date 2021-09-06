"""
MajorParser.py is a library built to receive information on Major Requirements

Contributors:
Calder Lund
"""

from ProgramParsing.AHS.MajorReq import AHSMajorReq
from ProgramParsing.ProgramParser.MajorParser import MajorParser
import pkg_resources
from bs4 import BeautifulSoup
from StringToNumber import StringToNumber
import re

class AHSMajorParser2021_2022(MajorParser):
    def __increment(self, i, information):
        i += 1
        while i < len(information) and information[i].replace(" ", "") == "":
            i += 1
        return i

    def _get_program(self):
        program = self.data.find_all("span", id="ctl00_contentMain_lblPageTitle")

        if program:
            program = program[0].contents[0].string
            if ", " in program and "Mental Health" not in program:
                program = program.split(", ")[1]

        return program

    def _get_relatedMajor(self, program):
        relatedMajor = self.data.find_all("span", id="ctl00_contentMain_lblBottomTitle")
        if relatedMajor:
            return relatedMajor[0].contents[0].string
        return ""

    def __get_courses(self, line):
        # Get courses from line
        line = line.replace("*", "").replace("/", " or ")

        coursesA = set(re.findall(r"[A-Z]{2,10}(?:\s[1-9][0-9][0-9][A-Z]?)?(?:\sor\s[A-Z]{2,10}(?:\s[1-9][0-9][0-9][A-Z]?)?){0,10}", line))
        coursesB = set(re.findall(r"(?:[A-Z]{2,10}\s)?[1-9][0-9][0-9][A-Z]?(?:\sor\s[A-Z]{2,10}(?:\s[1-9][0-9][0-9][A-Z]?)?){0,10}", line))
        courses = coursesA.union(coursesB)
        courses = list(courses)

        if ("One" in line and "from the following list" in line) or \
                re.findall(r"(One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|All) of", line):
            courses = [" or ".join(courses)]

        return courses

    def __append_requirement(self, line, majorReq):
        line = line.lower()

        if "elective" in line or "cluster" in line or \
            (len(majorReq.courseCodes.split(",")) > 1 and (majorReq.credits == 0.5 or
                                                           ("from" in line and "required" not in line))):
            majorReq.courseCodes = majorReq.courseCodes.replace(",", " or")

        codes = majorReq.courseCodes.split(", ")
        if len(line) > 250:
            line = line[:250]

        if len(codes) == 1 and majorReq.credits > 0.5:
            self.requirement.append(AHSMajorReq(codes[0].split(" or "), majorReq.programName, majorReq.majorName,
                                                self.additionalRequirement, majorReq.credits))
            self.requirement[-1].numberOfCourses = int(majorReq.credits * 2)

        else:
            for code in codes:
                self.requirement.append(AHSMajorReq(code.split(" or "), majorReq.programName, majorReq.majorName,
                                                    self.additionalRequirement, 0.5))


    def load_file(self, file, year):
        """
                Parse html file to gather a list of required courses for the major

                :return:
        """
        html = pkg_resources.resource_string(__name__, file)
        self.data = BeautifulSoup(html, 'html.parser')

        program = self._get_program()
        relatedMajor = self._get_relatedMajor(program)

        # Find all additional requirement
        self.additionalRequirement = self.getAdditionalRequirement()

        text = self.data.find("span", {'class': 'MainContent'}).get_text()
        text = text.replace("Recreation elective courses", "REC")
        text = text.replace("Free elective courses", "ELECTIVE")
        text = text.replace("Restricted elective courses", "RESTRICTED")
        text = text.replace("seminar", "SEMINAR")
        text = text.replace("Kinesiology elective courses", "KIN")
        text = text.replace("HLTH 480 (0.25 unit)", "HLTH 480")
        text = text.replace(" (see Laurier calendar)", "")
        text = re.sub(r"[1-9][0-9][0-9]-", "", text)
        information = text.split("\n")

        i = 0
        while i < len(information):
            line = information[i]
            if len(line) and line[0] == "*":
                i = self.__increment(i, information)
                continue
            if line == "Course Sequence" or line == "Note" or line == "Notes" or line == "General":
                break
            if "equired" in line or "unit" in line or len(re.findall(r"[A-Z]{2,10}", line)):
                majorReq = AHSMajorReq([], program, relatedMajor, self.additionalRequirement, "")
                if "lective" in line:
                    majorReq.condition = "or"
                # Create major reqs
                if "equired" in line or "unit" in line:
                    credits = re.findall(r"[0-9]+\.[0-9]+", line)
                    if len(credits) == 0:
                        num = line.lower().split()[0]
                        if num in StringToNumber._value2member_map_:
                            credits = StringToNumber[num]
                            majorReq.credits = float(credits/2)
                    else:
                        majorReq.credits = float(credits[0])
                    all_courses = set([])
                    if "Recreation and Sport Business elective courses" in line:
                        i += 4
                    j = i
                    if information[i].startswith("Note"):
                        i = self.__increment(i, information)
                        continue
                    while i < len(information) and not ((i > j and ("equired" in information[i] or
                                                                   "unit" in information[i] or
                                                                   (len(information[i]) and information[i][0] == "*")))):
                        courses = self.__get_courses(information[i])
                        all_courses = all_courses.union(courses)

                        isXof = re.findall(r"(One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|All) of", information[i])
                        if isXof:
                            if isXof[0].lower() in StringToNumber._value2member_map_:
                                majorReq.credits = 0.5 * StringToNumber(isXof[0].lower())

                        i = self.__increment(i, information)
                        if i < len(information) and (information[i] == "Course Sequence" or information[i] == "Notes" or information[i] == "General"):
                            break
                    if majorReq.credits and len(all_courses) and (len(all_courses) == 1 or len(all_courses) >= majorReq.credits):
                        if "RESTRICTED" in all_courses:
                            all_courses = ["RESTRICTED"]
                        majorReq.list = list(all_courses)
                        majorReq.update()
                        self.__append_requirement(line, majorReq)
                    if line == "Course Sequence" or line == "Note" or line == "Notes" or line == "General":
                        break
                    continue

                else:
                    # Get courses from line
                    courses = self.__get_courses(line)
                    if majorReq.credits and len(courses):
                        if "RESTRICTED" in courses:
                            courses = ["RESTRICTED"]
                        majorReq.list = courses
                        majorReq.update()
                        self.__append_requirement(line, majorReq)
                    i = self.__increment(i, information)
                    continue

            i = self.__increment(i, information)
