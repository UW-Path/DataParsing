"""
CourseParser.py is a library built to receive information on Major Requirements

Contributors:
Hao Wei Huang
Calder Lund
"""

from bs4 import BeautifulSoup
from ProgramParsing.Math.MajorReq import MathMajorReq
from ProgramParsing.ProgramParser.MajorParser import MajorParser
from StringToNumber import StringToNumber
import re
import pkg_resources


class MathMajorParser(MajorParser):
    def _get_program(self):
        program = self.data.find_all("span", id="ctl00_contentMain_lblBottomTitle")

        if program:
            program = program[0].contents[0].string
        else:
            #Exception for Table II data
            return "Table II"
        #Parsing the heading above the highlighted span
        #if major == degree req, spcialization, parse the highlighted span

        if "requirements" in program.lower() or "specializations" in program.lower() or "specialization" in program.lower():
            program = self.data.find_all("span", class_="pageTitle")
            program = str(program[0].contents[0])

        if "Overview and Degree Requirements" in program:
            program = program.replace(" Overview and Degree Requirements", "")

        #check for minor
        minor = self.data.find_all("span", class_="pageTitle")
        minor = str(minor[0].contents[0])

        if "minor" in str(minor).lower():
            program = minor

        return program
        # TODO: Need a case where this tile area is Degree Requirements

    def _require_all(self, list, major, relatedMajor, additional=None):
        for l in list:
            self.requirement.append(MathMajorReq([l], "All of", major, relatedMajor, self.additionalRequirement, 0))

    def _course_list(self, info, i, oneOf = False, allOf = False):
        list = []
        while i < len(info):

            line = info[i].strip().replace(" to ", "-")

            #Table II exception a bit hardcoded (info[i] == " ")

            #Computational Math case:
            if "Notes:" in line:
                break

            if line.startswith("Note") or line.startswith("(") or info[i] == "        ":
                i += 1
                continue

            #check if line is additional course
            # and list make sure theres at least one item in the 1,2,3, of
            if len(line.split(" ")) >= 2 and line.split(" ")[1] == "additional" and list:
                break

            rangeCourse = re.findall(r"[A-Z]+\s{0,1}[1-9][0-9][0-9]\s{0,1}-\s{0,1}[A-Z]+\s{0,1}[1-9][0-9][0-9]",
                                 line)
            courses = re.findall(r"\b[A-Z]{2,10}\b[^\s]*[^.]\b[0-9]{1,4}[A-Z]{0,1}\b", line)


            if rangeCourse:
                #TODO: Account for range CS 123-CS 345, excluding CS XXX
                # if oneOf or allOf:
                if allOf:
                    print("allof")
                for c in rangeCourse:
                    if c not in list:
                        list.append(c)
                # else: list.append(" or ".join(rangeCourse))
                i += 1
                continue

            if not courses:
                r = self._getLevelCourses(line)
                maj = ""

                majors = []
                for word in line.split(' '):
                    if ("Science" == word or "Mathematics" == word) and "Computational Mathematics advisor" not in line:
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
                                list.append(m + " " + r[0])  # don't assume grad courses for now
                    else:
                        for m in majors:
                            for level in r:
                                list.append(m + " " + level)
                    i+=1
                    continue
            # elif (maj and "distributed as follows:" not in line) or len(
            #         maj.split(", ")) > 1:  # prevent case "distrubted as follow:"
            #     # allow case chosen from BIOL, CHEM, EARTH, MNS, PHYS, or SCI:
            #     if maj == "MATHEMATICS": maj = "MATH"
            #     # SCIENCE - any level /Math
            #     list.append(maj)

            if not courses and list:
                # List has ended

                #this is to check if the parsing accidently have space unintentionally (the html is messed up)
                # for example:
                # All of:
                # CS 135
                # EMPTY LINE
                # CS 136

                if re.findall(r"(One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|All) (of|additional)", line) or i+1 == len(info):
                    #index out of range or it's one of /all of/ additional course (keyword that indicates new line)
                    break

                ## We want to capture CS 136 as well
                next_line = info[i+1].strip().replace(" to ", "-")

                if re.findall(r"^(One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|All)", next_line):
                    #index out of range or it's one of /all of/ additional course (keyword that indicates new line)
                    break

                courses = re.findall(r"\b[A-Z]{2,10}\b[^\s]*[^.]\b[0-9]{1,4}[A-Z]{0,1}\b", next_line)
                if courses:
                    #Next line is also course code so we don't break
                    i += 1
                    continue
                break

            if courses:
                if (oneOf and " or " not in line):
                    for c in courses:
                        if c not in list:
                            list.append(c)
                else:
                    #all of cases
                    list.append(", ".join(courses))
            i += 1
        return i, list

    def _additional_list(self, info, i, multiLine):
        list = []
        if multiLine:
            #"Two additional courses from"
            i += 1 #skip first line

            #specific for Mathematical Studies business option only
            isChunk = False
            #this part was implemnted for Joint PMATH when additional courses go on
            exception = ["one of", "two of", "three of", "four of", "five of", "six of", "seven of", "eight of", "nine of"]
            while i < len(info):
                if isChunk and info[i] == "":
                    #dont end for courses that have new lines in between additional
                    i += 1
                    continue
                if "\r" in info[i]: isChunk = True
                else: isChunk = False

                line = info[i].strip().replace(" to ", "-")
                if line.lower() in exception:
                    break

                foundPattern = False
                if "additional" in line:
                    break #search is over
                if line.startswith("Note") or line.startswith("("):
                    i += 1
                    continue

                ignoreCourses = [] #To prevent duplicate of ABC XXX-DEF XXX from single regex

                # range CS 389-CS 495
                courses = re.findall(r"[A-Z]+\s{0,1}[1-9][0-9][0-9]\s{0,1}-\s{0,1}[A-Z]+\s{0,1}[1-9][0-9][0-9]",
                                     line)
                if courses:
                    foundPattern = True
                    for course in courses:
                        course = course.strip("\n").strip("\r\n")
                        if not str(course).startswith("(") and course not in list:
                            list.append(course)
                            c = course.split("-")
                            for item in c:
                                item = item.strip()
                                ignoreCourses.append(item)
                else:
                    # find for another match cs 300-
                    maj = ""
                    match = self._getLevelCourses(str(line))

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
                            level = m.strip("\n")
                            level = level.strip("\r\n")
                            if "/" in maj:
                                list.append(maj.split("/")[0] + " " + level)
                                list.append(maj.split("/")[1] + " " + level)
                            else:
                                list.append(maj + " " + level)
                            #add CS 300- to ignore list for regex
                            level = level.replace("-", "")
                            ignoreCourses.append(maj + " " + level)

                # regular CS 135
                courses = re.findall(r"\b[A-Z]{2,10}\b[^\s]*[^.]\b[0-9]{1,4}[A-Z]{0,1}\b", line)
                #to find courses that says excluding CO 480
                exclude = re.findall(r"excluding \b[A-Z]{2,10}\b \b[0-9]{1,4}[A-Z]{0,1}\b", line)
                if exclude:
                    excludeCourse = exclude[0].replace("excluding ", "") #take course code
                    ignoreCourses.append(excludeCourse)
                if courses: foundPattern = True
                for course in courses:
                    if course not in ignoreCourses and course not in list:
                        list.append(course)


                if not foundPattern and list:
                    # List has ended
                    break
                i += 1

        else:
            line = info[i].strip().replace(" to ", "-")
            i += 1

            ignoreCourses = []  # To prevent duplicate of ABC XXX-DEF XXX from single regex

            #range CS 389-CS495
            courses = re.findall(r"[A-Z]+\s{0,1}[1-9][0-9][0-9]\s{0,1}-\s{0,1}[A-Z]+\s{0,1}[1-9][0-9][0-9]",line)
            if courses:
                for course in courses:
                    course = course.strip("\n").strip("\r\n")
                    if not str(course).startswith("(") and course not in list:
                        list.append(course)
                        c = course.split("-")
                        for item in c:
                            item = item.strip()
                            ignoreCourses.append(item)
            else:
                # find for another match cs 300-
                maj = ""
                match = self._getLevelCourses(str(line))

                for word in line.split(' '):
                    if word.isupper() or "math" in word or "non-math" in word:  # special case for "One additional 300- or 400-level math course.
                        maj = word.strip("\n").strip("\r\n").upper()
                        break

                if match:
                    for m in match:
                        level = m.strip("\n")
                        level = level.strip("\r\n")
                        # add CS 300- to ignore list for regex
                        if "/" in maj:
                            list.append(maj.split("/")[0] + " " + level)
                            list.append(maj.split("/")[1] + " " + level)
                        else:
                            list.append(maj + " " + level)
                        level = level.replace("-", "")
                        ignoreCourses.append(maj + " " + level)
                elif maj:
                    list.append(maj)  # Only indicate major but not level
                else:
                    #Four additional elective courses
                    list.append("Elective")

            # regular CS 135
            courses = re.findall(r"\b[A-Z]{2,10}\b[^\s]*[^.]\b[0-9]{1,4}[A-Z]{0,1}\b", line)
            # to find courses that says excluding CO 480
            exclude = re.findall(r"excluding \b[A-Z]{2,10}\b \b[0-9]{1,4}[A-Z]{0,1}\b", line)
            if exclude:
                excludeCourse = exclude[0].replace("excluding ", "")  # take course code
                ignoreCourses.append(excludeCourse)
            for course in courses:
                if course not in ignoreCourses and course not in list:
                    list.append(course)

        return i, list

    def is_additional(self, string):
        string = str(string).lower()
        if "recommended" in string:
            return False
        try:
            secondWord = str(string).split(" ")[1]
        except:
            return False
        if "additional" == secondWord:
            return True
        else: 
            return False

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

        try:
            information = self.data.find("span", {'class': 'MainContent'}).get_text().split("\n")
        except:
            #Table II exception
            information = self.data.find("body").get_text().split("\n")

        i = 0
        while i < len(information):
            l = information[i].strip().lower().replace("at least ", "")
            #special case to terminate CS
            if l.lower() == "elective breadth requirements" or l.lower() == "elective depth requirements":
                break

            if program == "Mathematics/Financial Analysis and Risk Management" and "specialization" in l:
                #We don't parse specialization for FARM
                break


            if l.startswith("one of"):
                i, list = self._course_list(information, i, True)
                if list:
                    self.requirement.append(MathMajorReq(list, "One of", program, relatedMajor, self.additionalRequirement))
            elif l.startswith("two of"):
                i, list = self._course_list(information, i)
                if list:
                    self.requirement.append(MathMajorReq(list, "Two of", program, relatedMajor, self.additionalRequirement))
            elif l.startswith("three of"):
                i, list = self._course_list(information, i)
                if list:
                    self.requirement.append(MathMajorReq(list, "Three of", program, relatedMajor, self.additionalRequirement))
            elif l.startswith("four of"):
                i, list = self._course_list(information, i)
                if list:
                    self.requirement.append(MathMajorReq(list, "Four of", program, relatedMajor, self.additionalRequirement))
            elif l.startswith("five of"):
                i, list = self._course_list(information, i)
                if list:
                    self.requirement.append(MathMajorReq(list, "Five of", program, relatedMajor, self.additionalRequirement))
            elif l.startswith("six of"):
                i, list = self._course_list(information, i)
                if list:
                    self.requirement.append(MathMajorReq(list, "Six of", program, relatedMajor, self.additionalRequirement))
            elif l.startswith("seven of"):
                i, list = self._course_list(information, i)
                if list:
                    self.requirement.append(MathMajorReq(list, "Seven of", program, relatedMajor, self.additionalRequirement))
            elif l.startswith("eight of"):
                i, list = self._course_list(information, i)
                if list:
                    self.requirement.append(MathMajorReq(list, "Eight of", program, relatedMajor, self.additionalRequirement))
            elif l.startswith("nine of"):
                i, list = self._course_list(information, i)
                if list:
                    self.requirement.append(MathMajorReq(list, "Nine of", program, relatedMajor, self.additionalRequirement))
            elif l.startswith("all of"):
                i, list = self._course_list(information, i, allOf=True)
                if list:
                    self._require_all(list, program, relatedMajor)
            elif (self.is_additional(l) or self._stringIsNumber(l)) \
                    and "excluding the following" not in l: #Three 400- Level courses
                number_additional_string = l.split(' ')[0]
                number_additional = StringToNumber[number_additional_string].value
                if not isinstance(number_additional, int):
                    number_additional = number_additional[0]
                #check if one sentence are multiple
                if "." in information[i]:
                    i, list = self._additional_list(information, i, False)
                else:
                    i, list = self._additional_list(information, i, True)
                # need to check if number_additional is an INT
                if list:
                    self.requirement.append(MathMajorReq(list, "Additional", program, relatedMajor, self.additionalRequirement, number_additional))
            elif "non-math" in l:
                # try to see if the second word is a number, if first is a number then the case before would capture
                number_additional = 0
                if "non-math units" in l:
                    units = True
                else:
                    units = False

                l = l.split(" ")
                try:
                    if units:
                        number_additional = float(l[1]) * 2
                    else:
                        #assume its courses
                        number_additional = float(l[1])
                except:
                    print("Skip, this does not satisfy non math credits")
                    i += 1
                    continue
                self.requirement.append(
                    MathMajorReq(["NON-MATH"], "Additional", program, relatedMajor, self.additionalRequirement,
                                 number_additional))
                i+=1

            elif "units" in l and ":" not in l:
                try:
                    #3.5 units of AMATH/PHYS electives, at least 1.0 unit of which are at the 300- or 400-level in Mathematical Physics
                    number_additional = float(l.split(" ")[0]) * 2
                    i, list = self._additional_list(information, i, False)

                    if list:
                        self.requirement.append(
                            MathMajorReq(list, "Additional", program, relatedMajor, self.additionalRequirement,
                                         number_additional))
                except:
                    #skip
                    i += 1


            else:
                i += 1
