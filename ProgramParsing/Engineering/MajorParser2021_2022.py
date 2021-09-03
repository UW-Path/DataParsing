"""
CourseParser.py is a library built to receive information on Major Requirements

Contributors:
Hao Wei Huang
"""

from bs4 import BeautifulSoup
from ProgramParsing.Engineering.MajorReq import EngineeringMajorReq
from ProgramParsing.ProgramParser.MajorParser import MajorParser
import re
import pkg_resources
from math import ceil
from Database.DatabaseReceiver import DatabaseReceiver
from StringToNumber import StringToNumber


class EngineeringMajorParser2021_2022(MajorParser):
    def _get_program(self):
        program = self.data.find_all("span", id="ctl00_contentMain_lblPageTitle")

        if program:
            #Honours Biochemistry, Biotechnology Specialization format then take second
            program = program[0].contents[0].string
            if ", " in program:
                program = program.split(", ")[1]

        return program
        # TODO: Need a case where this tile area is Degree Requirements

    def _course_list(self, line, oneOf = False):
        list = []
        if "Communication Elective" in line:
            return ["Communication Elective"]
        line = line.strip().replace(" to ", "-").replace("Technical Electives", "TE").replace("Technical Elective", "TE")
        line = line.replace("Complementary Studies Elective", "CSE").replace("Complementary Studies Electives", "CSE")

        d = dict() #dictionary to keep track of courses

        if line.startswith("Note") or line.startswith("("):
            return []

        if "WKRPT" in line or "ECE 101" in line:
            return []

        rangeCourse = re.findall(r"[A-Z]+\s{0,1}[1-9][0-9][0-9]\s{0,1}-\s{0,1}[A-Z]+\s{0,1}[1-9][0-9][0-9]",
                             line)
        courses = re.findall(r"\b[A-Z]{2,10}\b[^\s]*[^.]\b[0-9]{1,4}[A-Z]{0,1}", line)

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
                    #Avoid weird symbol like ‡
                    if "CSE" in temp:
                        temp = "CSE"
                    elif "TE" in temp:
                        temp = "TE"

                    if temp not in majors:
                        majors.append(temp)

            maj = ", ".join(majors)
            if maj:
                list.append(maj)

        if not list:
            if "Elective" in line or "electives" in line:
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
            self.requirement_dict[((course), 1, major, relatedMajor, additionalRequirement, 0.5)] += 1

    def get_table(self, data):
        tables = data.find_all("table")
        for table in  tables:
            tr = table.find("tr")
            th = tr.find("th")
            if "Term" in th.text:
                return table
        return None

    def get_text(self, td):
        #filter out subscript
        INVALID_TAGS = ['sup']

        for tag in td.findAll(True):
            if tag.name in INVALID_TAGS:
                tag.replaceWith("")
        return td.text

    def insert_mech_eng(self, line, program, relatedMajor, term):
        line = line.split(",")
        for req in line:
            number_additional = 1
            req = req.lstrip()
            if str(req.split(" ")[0]).isdigit():
                number_additional = int(req.split(" ")[0])
            list = self._course_list(req)
            if list:
                credits = self._count_credits(list) / len(list) * number_additional
                self.requirement_dict[(tuple(list), number_additional, program, relatedMajor, term, credits)] += 1

    def load_file(self, file, year):
        """
                Parse html file to gather a list of required courses for the major

                :return:
        """

        html = pkg_resources.resource_string(__name__, file)
        self.data = BeautifulSoup(html, 'html.parser')

        program = self._get_program()

        # Engineering only has majors
        relatedMajor = program

        #check if it has a table format

        information = self.data.find("span", {'class': 'MainContent'})

        table = self.get_table(information)

        if table:
            #search for courses here
            # terms = ["1A", "1B", "2A", "2B", "3A", "3B", "4A", "4B"]
            term = ""
            tbody = table.find("tbody")
            trs = tbody.find_all("tr")
            i = 0
            while i < len(trs):
                tr = trs[i]
                tds = tr.find_all("td")
                #special case for management eng
                th = tr.find("th")
                if th:
                    t = th.text
                else:
                    t = self.get_text(tds[0])


                isTerm = re.findall(r"\b(?:1A|1B|2A|2B|3A|3B|4A|4B)\b", t)
                if isTerm: # and isTerm[0] in terms:
                    term = isTerm[0]
                    #special case mech eng
                    if program == "Mechanical Engineering":
                        self.insert_mech_eng(self.get_text(tds[1]), program, relatedMajor, term)
                        i+=1
                        continue

                    if th:
                        #special case for management eng
                        list = self._course_list(self.get_text(tds[0]))
                    else:
                        list = self._course_list(self.get_text(tds[1]))

                    # ECE 101A/B/C/D or WRKT has empty list
                    if list:
                        credits = self._count_credits(list)
                        self.requirement_dict[(tuple(list), 1, program, relatedMajor, term, credits)] += 1
                    i+= 1
                    continue
                elif "Work Term" in t:
                    term ="" #stop searching

                if (term == ""):
                    i+=1
                    continue
                else:
                    l = str(t).lower()
                    if l.startswith("choose"):
                        #ECE Special
                        try:
                            number_additional_string = l.split(' ')[1]
                            number_additional = StringToNumber[number_additional_string].value
                            if not isinstance(number_additional, int):
                                number_additional = number_additional[0]
                        except:
                            #error occured skip
                            i+=1
                            continue
                        if "additional course" in l:
                            # one block of text
                            list = self._course_list(t)
                            if list:
                                credits = self._count_credits(list)/len(list)*number_additional
                                self.requirement_dict[(tuple(list), number_additional, program, relatedMajor, term, credits)] += 1
                            i += 1
                            continue
                        else:
                            line = ""
                            i+=1
                            while i < len(trs):
                                tr = trs[i]
                                tds = tr.find_all("td")
                                t = self.get_text(tds[0])
                                isTerm = re.findall(r"\b(?:1A|1B|2A|2B|3A|3B|4A|4B)\b", t)
                                if "Work Term" in t or isTerm:
                                    break
                                elif "Choose" in t:
                                    break
                                elif len(t.strip().split(" ")) > 2:
                                    #should just be a course code
                                    break
                                else:
                                    line += t + ", "
                                i += 1

                            list = self._course_list(line)
                            if list:
                                credits = self._count_credits(list) / len(list) * number_additional
                                self.requirement_dict[(tuple(list), number_additional, program, relatedMajor, term, credits)] += 1
                            continue
                    else:
                        noOfCourse = 1
                        if l.startswith("two"):
                            noOfCourse = 2
                        elif l.startswith("three"):
                            noOfCourse = 3
                        elif l.startswith("four"):
                            noOfCourse = 4
                        elif l.startswith("five"):
                            noOfCourse = 5
                        elif l.startswith("six"):
                            noOfCourse = 6

                        #special for nano eng
                        if "laboratory" in l and "from:" in l:
                            line = ""
                            i += 1
                            while i < len(trs):
                                tr = trs[i]
                                tds = tr.find_all("td")
                                t = self.get_text(tds[0])
                                isTerm = re.findall(r"\b(?:1A|1B|2A|2B|3A|3B|4A|4B)\b", t)
                                if "Work Term" in t or isTerm:
                                    break
                                elif "Laboratory" not in t:
                                    # should just be a course code
                                    break
                                else:
                                    line += t + ", "
                                i += 1

                            list = self._course_list(line)
                            if list:
                                credits = self._count_credits(list) / len(list) * noOfCourse
                                self.requirement_dict[(tuple(list), noOfCourse, program, relatedMajor, term, credits)] += 1
                            continue


                        #parse course
                        list = self._course_list(self.get_text(tds[0]))
                        if list:
                            credits = self._count_credits(list) / len(list) * noOfCourse
                            self.requirement_dict[(tuple(list), noOfCourse, program, relatedMajor, term, credits)] += 1
                        i += 1

        else:
            i = 0
            information = information.text.split("\n")
            term = ""
            #terminate after 4B is ran

            while i < len(information):
                line = str(information[i]).lstrip().rstrip()
                #initialize term

                isTerm = re.findall(r"(1A|1B|2A|2B|3A|3B|4A|4B) (\((Spring|Winter|Fall)\))", line)
                if "Technical Elective List" in line:
                    #special case for geologt
                    term = ""
                elif isTerm:
                    term = isTerm[0][0]
                    if term == "4B" and  information[i+1].strip() == "":
                        #if next is empty line we skip
                        i += 1


                elif term == "4B" and (line=="Electives" or line == ""):
                    #10 is aprox, Electives case for arch eng
                    break
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
                        self.requirement_dict[(tuple(list), number_additional, program, relatedMajor, term, credits)] += 1
                i += 1

        self.convert_dict_to_list(EngineeringMajorReq)
