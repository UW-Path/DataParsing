"""
CourseParser.py is a library built to receive information on Major Requirements

Contributors:
Hao Wei Huang
Calder Lund
"""

from bs4 import BeautifulSoup
from ProgramParsing.Arts.MajorReq import ArtsMajorReq
from ProgramParsing.ProgramParser.MajorParser import MajorParser
import re
import pkg_resources
from math import ceil
from Database.DatabaseReceiver import DatabaseReceiver
from StringToNumber import StringToNumber


class ArtsMajorParser2021_2022(MajorParser):
    def _get_program(self):
        program = self.data.find_all("span", id="ctl00_contentMain_lblPageTitle")

        if program:
            #Honours Biochemistry, Biotechnology Specialization format then take second
            program = program[0].contents[0].string
            if ", " in program:
                program = program.split(", ")[1]

        if program == "Bachelor of Arts Breadth Requirements":
            program = "Bachelor of Arts"


        return program
        # TODO: Need a case where this tile area is Degree Requirements

    def _get_relatedMajor(self, program):
        relatedMajor = self.data.find_all("span", id="ctl00_contentMain_lblBottomTitle")
        if relatedMajor:
            relatedMajor = relatedMajor[0].contents[0].string
        else:
            return ""

        if "Academic Plans and Requirements" in relatedMajor:
            # check if program is minor
            if "minor" in program.lower():
                program = program.replace(" Minor", "")
            return program
        else:
            return relatedMajor

    def _course_list(self, line, oneOf, additional):
        list = []
        line = line.strip().replace(" to ", "-")

        d = dict() #dictionary to keep track of courses

        if line.startswith("Note") or line.startswith("("):
            return []


        courses = re.findall(r"\b[A-Z]{2,10}\b[^\s]*[^.]\b[0-9]{1,4}[A-Z]{0,1}\b", line)


        if courses:
            for c in courses:
                if c not in d:
                    list.append(c)

        if not list:
            r = self._getLevelCourses(line)
            maj = ""
            if "program elective" in line:
                maj = "Program Elective" #extra case for material nanosci
            else:
                majors = []
                for word in line.split(' '):
                    if "Science" == word or "Mathematics" == word:
                        maj = word.strip("\n").strip("\r\n").upper()
                        maj = maj.replace(",", "")
                        break
                    elif word.isupper():
                        temp = word.replace(",", "")
                        if temp not in majors:
                            majors.append(temp)
                if maj == "":
                    maj = ", ".join(majors)
            if r and maj:
                majors = maj.split(", ")
                if len(majors) == 1 and "lab" in line:
                    #PHYSC lab: Special case
                    majors[0] += " LAB"
                if "or higher" in line or "or above" in line:
                    for m in majors:
                        if r[0] == "100-":
                            list.append(m + " " + r[0])
                            list.append(m + " 200-")
                            list.append(m + " 300-")
                            list.append(m + " 400-")
                        elif r[0] == "200-":
                            list.append(m + " " + r[0])
                            list.append(m + " 300-")
                            list.append(m + " 400-")
                        elif r[0] == "300-":
                            list.append(m + " " + r[0])
                            list.append(m + " 400-")
                        elif r[0] == "400-":
                            list.append(m + " " + r[0]) #don't assume grad courses for now
                else:
                    for m in majors:
                        for level in r:
                            list.append(m + " " + level)
            elif maj and ":" not in line or len(maj.split(", ")) > 1: #prevent case "with the following conditions:"
                # allow case chosen from BIOL, CHEM, EARTH, MNS, PHYS, or SCI:
                list.append(maj)
            if len(r) > 1:
                print("ERROR more than one match 200- found")

        if additional:
            line = line.split(" ")
            for word in line:
                try:
                    # find first float
                    credits = float(word)
                except:
                    print("exception")
        elif oneOf:
            credits = 0.5
        else:
            credits = len(list) * 0.5

        return list, oneOf,credits


    def _require_all(self, list, major, relatedMajor, additionalRequirement):
        #TODO: Match with database credits
        #TODO: Dafault as 0.5 credits
        for course in list:
            self.requirement.append(ArtsMajorReq([course], 1, major, relatedMajor, additionalRequirement, 0.5))

    def load_file(self, file, year):
        """
                Parse html file to gather a list of required courses for the major

                :return:
        """
        html = pkg_resources.resource_string(__name__, file)
        self.data = BeautifulSoup(html, 'html.parser')

        program = self._get_program()

        # find the major related to specializations and options
        relatedMajor = self._get_relatedMajor(program)
        if program == "Degree Requirements":
            program = relatedMajor

        # Find all additional requirement
        self.additionalRequirement = self.getAdditionalRequirement()

        information = self.data.find("span", {'class': 'MainContent'}) \
        #check if arts breadth req
        if program == "Bachelor of Arts":
            rows  = information.find("table").find("tbody").find_all("tr")
            self.additionalRequirement = "Arts Plan"
            # Undergrad Comm req, special case
            self.requirement.append(ArtsMajorReq(["ARTS 130"], 1, program, relatedMajor, self.additionalRequirement, 0.5))
            self.requirement.append(ArtsMajorReq(["ARTS 140"], 1, program, relatedMajor, self.additionalRequirement, 0.5))

            for row in rows:
                credits = 0
                numCourse = 0 #initializing ariable
                cells = row.find_all("td")
                try:
                    # 1.0 units
                    credits = float(cells[1].text.split(" ")[0])
                    numCourse = credits/0.5
                    courseMajorLink = cells[2].find_all("a")  # condition for breadth
                    list = [c.text for c in courseMajorLink]

                    self.requirement.append(
                        ArtsMajorReq(list, numCourse, program, relatedMajor, self.additionalRequirement, credits))
                except:
                    print("Error has occured")





        else:
            information = information.get_text().split("\n")

            i = 0
            while i < len(information):
                line = information[i]
                line = line.strip()
                if "Notes" in line:
                    break

                if "Successful completion" in line:
                    i += 1 # special case
                    continue

                elif line.lower() == "undergraduate communication requirement":
                    # Undergrad Comm req, special case
                    self.requirement.append(ArtsMajorReq(["ARTS 130"], 1, program, relatedMajor, self.additionalRequirement, 0.5))
                    self.requirement.append(ArtsMajorReq(["ARTS 140"], 1, program, relatedMajor, self.additionalRequirement, 0.5))
                    i+= 1
                    continue
                elif "language courses" in line and self._stringIsNumber(line):
                    number_additional_string = line.split(' ')[0].lower()
                    number_additional = StringToNumber[number_additional_string].value
                    if not isinstance(number_additional, int):
                        number_additional = number_additional[0]
                    credits = number_additional * 0.5
                    self.requirement.append(
                        ArtsMajorReq(["LANGUAGE"], number_additional, program, relatedMajor, self.additionalRequirement, credits))


                try:
                    oneOf = "one of" in line
                    additional = False
                    if "additional" in line:
                        additional = True

                    list, oneOf, credits = self._course_list(line,oneOf, additional)
                    numCourse = credits/0.5
                    if list:
                        if oneOf:
                            self.requirement.append(ArtsMajorReq(list, numCourse, program, relatedMajor, self.additionalRequirement, credits))

                        else:
                            self._require_all(list, program, relatedMajor, self.additionalRequirement)

                except (RuntimeError):
                    print(RuntimeError)
                    pass
                    #not parsable
                i += 1

