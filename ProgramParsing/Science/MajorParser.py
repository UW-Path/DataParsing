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
from Database.DatabaseReceiver import DatabaseReceiver


class ScienceMajorParser(MajorParser):
    def _get_program(self):
        program = self.data.find_all("span", id="ctl00_contentMain_lblPageTitle")

        if program:
            #Honours Biochemistry, Biotechnology Specialization format then take second
            program = program[0].contents[0].string
            if ", " in program:
                program = program.split(", ")[1]

        #check for minor
        minor = self.data.find_all("span", class_="pageTitle")
        minor = str(minor[0].contents[0])

        if "minor" in str(minor).lower():
            program = minor

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

    def _course_list(self, line, credit, oneOf = False):
        list = []
        line = line.strip().replace(" to ", "-")

        d = dict() #dictionary to keep track of courses

        if line.startswith("Note") or line.startswith("("):
            return []


        rangeCourse = re.findall(r"[A-Z]+\s{0,1}[1-9][0-9][0-9]\s{0,1}-\s{0,1}[A-Z]+\s{0,1}[1-9][0-9][0-9]",
                             line)
        courses = re.findall(r"\b[A-Z]{2,10}\b[^\s]*[^.]\b[0-9]{1,4}[A-Z]{0,1}\b", line)

        orCourse = re.findall(r"\b(?<!\/)[A-Z]{2,10}\b \b[0-9]{1,4}[A-Z]{0,1}\b or \b[A-Z]{2,10}\b \b[0-9]{1,4}[A-Z]{0,1}\b", line)

        if orCourse:
            # CS 135 or CS XXX
            for oC in orCourse:
                c = oC.split(" or ")
                d[c[0]] = True
                d[c[1]] = True
                list.append(oC.replace(" or ", ", "))

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
            r = self._getLevelCourses(line)
            maj = ""
            if "program elective" in line:
                maj = "Program Elective" #extra case for material nanosci
            else:
                majors = []
                for word in line.split(' '):
                    if "Science" == word or "Mathematics" == word or "Arts" == word or "Environment" ==word:
                        maj = word.strip("\n").strip("\r\n").upper()
                        maj = maj.replace(",", "")
                        break
                    elif word.isupper():
                        temp = word.replace(",", "")
                        if temp not in majors:
                            majors.append(temp)
                if maj == "":
                    maj = ", ".join(majors)

            if maj == "" and  "lecture" in line: #case for chemistry and more where we need to include lecture as electives
                if self._get_program() != "Honours Science and Aviation":
                    #Don't want to include Aviation special case (refer to the page)
                    maj ="Elective"

            if r and maj:
                majors = maj.split(", ")
                if len(majors) == 1 and "lab" and majors[0] != "Elective" in line:
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
            elif maj and "any level" in line:
                list.append(maj + " 100-")
                list.append(maj + " 200-")
                list.append(maj + " 300-")
                list.append(maj + " 400-")
            elif (maj and "distributed as follows:" not in line) or len(maj.split(", ")) > 1: #prevent case "distrubted as follow:"
                # allow case chosen from BIOL, CHEM, EARTH, MNS, PHYS, or SCI:
                if maj == "MATHEMATICS": maj = "MATH"
                #SCIENCE - any level /Math
                elif "lab" in line and maj != "Elective":
                    maj += " LAB"
                list.append(maj)
            if len(r) > 1:
                print("ERROR more than one match 200- found")

        if list:
            for course in list:
                if "-" in course:
                    return list, False
                elif "ACTSC, AMATH, CO, CS, MATH, PMATH, STAT" in course:
                    return list, False #hardcoded to prevent "insertAll"

            c = self._count_credits(list)
            # if 0 is returned the list has general courses: SCIENCE,MATH
            if (credit == c or len(list) == 1) and c != 0:
                #Note: 1 is coded as a special case. Not perfect accuracy in terms of credit count
                return list, True

        return list, False

    def _count_credits(self,list):
        dbc = DatabaseReceiver()
        count = 0
        for course in list:
            courseNum = ""
            if len(course.split(" ")) > 1:
                # Exception for SCIENCE -any level
                courseNum = course.split(" ")[1]
            else:
                #This means that it is a general course, should never be in All of option
                return 0
            if "L" in courseNum:
                try:
                    count += float(dbc.select_course_credit(course))
                except:
                    print(course)
                    count += 0.25
            else:
                count += 0.5
        dbc.close()
        return float(count)

    def _require_all(self, list, major, relatedMajor, additionalRequirement):
        #TODO: Match with database credits
        #TODO: Dafault as 0.5 credits
        dbc = DatabaseReceiver()

        for course in list:
            if "L" in course:
                try:
                    credit = dbc.select_course_credit(course)
                except:
                    print("Course not found. Default is 0.5 credit")
                    credit = 0.5
            else: credit = 0.5
            self.requirement.append(ScienceMajorReq([course], 1, major, relatedMajor, additionalRequirement, credit))

        dbc.close()

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

        # Find all additional requirement
        self.additionalRequirement = self.getAdditionalRequirement()

        information = self.data.find("span", {'class': 'MainContent'}).get_text().split("\n")

        i = 0
        while i < len(information):
            line = information[i].replace("a minimum of", "")

            if "Recommended Course Sequence" in line:
                break
            if "\r" in line:
                #fix for Astrophysics Minor where enter key was used to link two courses
                line += information[i + 1]
                i += 1

            line = line.strip()


            if "must" in line and ":" not in line:
                #Condition for must complete... additional conditions
                #Example: '0.5 unit must be 200-level or higher'
                #However '4.0 units must be chosen from List A: ..."

                #special case for 1.5 elective units; must be 0.5 unit lecture courses (we want this)
                if "elective" in line:
                    try:
                        float(line.split(" ")[0])
                    except:
                        i += 1
                        continue
                else:
                    i += 1
                    continue
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
                elif "elective" in line.split(' ')[1] and ":" not in line or "chosen from any subject" in line or "chosen from any 0.5 unit courses" in line \
                        or "from any 0.25 or 0.5 unit courses" in line:
                    list.append("Elective")
                    self.requirement.append(ScienceMajorReq(list, numCourse, program, relatedMajor, self.additionalRequirement, credits))

            except (RuntimeError):
                print(RuntimeError)
                pass
                #not parsable
            i += 1


