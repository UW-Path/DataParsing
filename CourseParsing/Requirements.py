"""
Requirements is an object class that parses and tracks information
pertaining to prerequisites and anti-requisites.

Contributors:
Calder Lund
"""

import re
from CourseParsing.AsciiTranslator import get_char, get_index
from CourseParsing.ParseTree import remove_dup_bracket, translate_to_python, denote_coreqs, fix_logic


class Prereqs:
    def __init__(self):
        self.prereqs = []
        self.min_grade = []  # Parallel list to prereqs
        self.not_open = []
        self.students_only = []
        self.min_level = "1A"

        self.logic = ""
        self.courses = []

    def letters_to_courses(self, options, courses):
        """
        Depreciated
        """
        output = ""
        for option in options:
            for char in option:
                output += courses[get_index(char)] + " & "
            output = output[:-3] + " | "
        output = output[:-3]
        return output

    def load_prereqs(self, prereqs, course_code=""):
        """
        Parses the necessary prerequisite data.

        :param prereqs: string
        :return: boolean
        """
        if isinstance(prereqs, str):
            prereqs = prereqs.replace("Prereq: ", "")
            prereqs = prereqs.replace("Coreq: ", "***")
            prereqs_alt = re.split("[;.]", prereqs)

            # Remove single upper characters
            prereqs = re.sub("^[A-Z] ", "", prereqs)
            prereqs = re.sub("([^A-Za-z0-9])[A-Z] ", "\1 ", prereqs)

            # Deal with corequisite options in the prereq by deonoting all courses after ### as a coreq
            prereqs = re.sub("[Cc]o(?:-)?req(?:uisite)?(?::)?", "###", prereqs)

            # Convert to numbers for parsing readability
            prereqs = prereqs.replace("One ", "1 ").replace("one ", "1 ").replace("0.50", "1").replace("0.5", "1")
            prereqs = prereqs.replace("Two ", "2 ").replace("two ", "2 ").replace("1.00", "2").replace("1.0", "2")
            prereqs = prereqs.replace("Three ", "3 ").replace("three ", "3 ").replace("1.50", "3").replace("1.5", "3")
            prereqs = prereqs.replace("Four ", "4 ").replace("four ", "4 ").replace("2.00", "4").replace("2.0", "4")
            prereqs = prereqs.replace("Five ", "5 ").replace("five ", "5 ").replace("2.50", "5").replace("2.5", "5")
            prereqs = prereqs.replace("Six ", "6 ").replace("six ", "6 ").replace("3.00", "6").replace("3.0", "6")

            # Remove all numbers longer than 3 digits
            prereqs = re.sub("[0-9][0-9][0-9][0-9]+", "", prereqs)

            # <year> year ABC becomes ABC 1000
            prereqs = re.sub("first year ([A-Z][A-Z]+)", r"\1 1000", prereqs)
            prereqs = re.sub("second year ([A-Z][A-Z]+)", r"\1 2000", prereqs)
            prereqs = re.sub("third year ([A-Z][A-Z]+)", r"\1 3000", prereqs)
            prereqs = re.sub("fourth year ([A-Z][A-Z]+)", r"\1 4000", prereqs)

            # Remove all words that are separated with / that aren't part of courses
            prereqs = re.sub(" [a-zA-Z\\-]*[a-z][a-zA-Z\\-]*/[a-zA-Z\\-]+", "", prereqs)
            prereqs = re.sub(" [a-zA-Z\\-]+/[a-zA-Z\\-]*[a-z][a-zA-Z\\-]*", "", prereqs)

            # Replace brackets with < >
            prereqs = prereqs.replace("(", " < ").replace(")", " > ")

            # Convert and's into &
            prereqs = re.sub("[^A-Za-z]and", " & ", prereqs)
            # Convert or's into |
            prereqs = re.sub("([0-9>])\\s*or\\s*([A-Z0-9<])", r"\1 | \2", prereqs)
            prereqs = re.sub("([^A-Za-z])\\s*or", r"\1 | ", prereqs)

            # Replace all course slashes with < course /| course ... >
            pattern = "([A-Z]+[ ]?(?:[0-9][0-9][0-9][A-Z0]?)?|(?:[A-Z]+)?[ ]?[0-9][0-9][0-9][A-Z0]?)/"
            replace = r" < \1 /| \2 /| \3 /| \4 /| \5 /| \6 /| \7 /| \8 /| \9 >"
            for i in range(9, 1, -1):
                m_pattern = (i * pattern)[:-1]
                prereqs = re.sub(m_pattern, replace, prereqs)
                replace = replace[:-8] + replace[-2:]

            # X00-level becomes X000
            prereqs = prereqs.replace("-level", "0")

            # Remove -
            prereqs = prereqs.replace("-", " ")

            # Any XXX course becomes XXX 0000
            prereqs = re.sub("[Aa]ny ([A-Z]+)(?: course)?", r"\1 0000", prereqs)
            prereqs = re.sub("([1-9]) unit(?:s)? (?:in|of) ([A-Z]+)", r"\1 \2 0000", prereqs)

            # Add not condition for antireqs in prereq
            prereqs = re.sub("Not open to students who(?: have)? received credit for ", "~", prereqs)

            # Remove PD
            prereqs = re.sub("PD [1-9][0-9]", "", prereqs)

            # Remove entire block that includes "Open only ...;" and "Level at ...;"
            prereqs = re.sub("((?:Open only to students in .+[.;])|"
                             "(?:[Ll]ev(?:el)? at [^.;>&<,]+))", " ", prereqs)

            # Remove XX% and 2A like text
            prereqs = re.sub("((?:[1-9][0-9]%)|"
                             "(?:[^0-9][1-9][A-Z]))", " ",
                             prereqs)

            # Remove all words
            prereqs = re.sub("[a-zA-Z\\-]*[a-z][a-zA-Z\\-]*", "", prereqs)

            # Replace all "; |" with "| ;"
            prereqs = re.sub(";\\s*\\|", " | ;", prereqs)

            # Replace . with &
            prereqs = prereqs.replace(".", " & ")

            # Clean spaces
            prereqs = re.sub("\\s+", " ", prereqs)

            # Strip < from end, > from start
            while True:
                old_prereqs = prereqs
                while prereqs.endswith(" <"):
                    prereqs = prereqs[:-2]
                while prereqs.startswith("> "):
                    prereqs = prereqs[2:]

                # Replace [block] | ; [block] with [block] | [block]
                prereqs = re.sub("([^;]+)\\|\\s*;([^;]+)", r"< \1 > | < \2 >", prereqs).strip(" &|,/;")

                # Replace [block] ; [block] with [block] & [block]
                prereqs = re.sub("([^;]+);([^;]+)", r"< \1 > & < \2 >", prereqs).strip(" &|,/;")

                # If changes cannot be made, exit loop
                if prereqs == old_prereqs:
                    break

            # Clean spaces
            prereqs = re.sub("\\s+", " ", prereqs)

            # Reverse 2000 XXX to XXX 2000
            prereqs = re.sub("([0-9]{4})\\s([A-Z]+)", r"\2 \1", prereqs)

            # Replace "CS 135 | 145 & MATH 135" with "CS 135 /| 145 & MATH 135"
            while True:
                new_prereqs = re.sub("([A-Z]+\\s*[0-9]{3}[A-Z0]?\\s*)\\|(\\s*[0-9]{3}[A-Z0]?)", r"\1 /| \2", prereqs)
                if new_prereqs == prereqs:
                    break
                else:
                    prereqs = new_prereqs

            # Find all courses and their indexes
            grep = "[A-Z]+ /\\||(?:[A-Z]+[ ]?)?[0-9][0-9][0-9][A-Z0]?|[A-Z][A-Z]+"
            courses = re.findall(grep, prereqs)
            indexes = [(m.start(0), m.end(0)) for m in
                       re.finditer(grep, prereqs)]

            # Generate new course codes by turning ["CS 135", "145"] into ["CS 135", "CS 145"]
            new_courses = []
            code = ""
            for i, course in enumerate(courses):
                new_number = re.findall("[0-9][0-9][0-9][A-Z0]?", course)
                course = re.sub("[0-9][0-9][0-9][A-Z0]?", "", course)
                new_code = re.findall("[A-Z]+", course)
                if len(new_code):
                    code = new_code[0]
                if len(new_number):
                    number = new_number[0]
                else:
                    number = ""
                course = code + " " + number
                new_courses.append(course)

            # Loop backwards to replace each course with a respective letter
            courses = new_courses
            for i in range(len(courses)-1, -1, -1):

                # If course had no number, use the number from lookahead
                if courses[i].endswith(" "):
                    if i < len(courses)-1:
                        courses[i] += re.findall("[0-9][0-9][0-9][A-Z0]?", courses[i+1])[0]
                    else:
                        courses[i] += "0000"

                # If the course ahead ends with a letter, the current does not and they have different codes, add the
                # letter from lookahead to the end if the current course.
                elif i < len(courses)-1 and courses[i][-1] in "1234567890" and \
                        courses[i+1][-1] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" and \
                        courses[i][-3:] != courses[i+1][-4:-1] and prereqs[indexes[i][1]+1:indexes[i][1]+3] == "/|":
                    courses[i] += courses[i+1][-1]

                # Generate a condition string for the current course to the next
                string = " "
                if prereqs[indexes[i][1]-1] == "|":
                    if prereqs[indexes[i][1]-2] == "/":
                        string = " /| "
                    else:
                        string = " | "

                # Convert course to letter
                prereqs = prereqs[:indexes[i][0]] + " " + get_char(i) + string + prereqs[indexes[i][1]:]

            # Any cases of courses without codes get assigned the same as the original course
            for i in range(len(courses)):
                if courses[i][0] == " ":
                    courses[i] = course_code + courses[i]

            # Convert , | to /|
            prereqs = prereqs.strip(" &|,").replace(", |", "/|")

            # Clean spaces
            prereqs = re.sub("\\s+", " ", prereqs)

            # Replace "2 A , < B & C > /| D" with "< 2 A | < B & C > | D >"
            comma_indices = [(m.start(0), m.end(0)) for m in
                             re.finditer("[1-9] ([A-Za-z]|< [^>]+ >)(?:\\s*(,|/\\||\\|)\\s*([A-Za-z]|< [^>]+ >))+", prereqs)]
            for i in range(len(comma_indices)-1, -1, -1):
                start, end = comma_indices[i]
                prereqs = prereqs[:start] + " < " + prereqs[start:end].replace(",", " | ") + \
                          " > " + prereqs[end:]

            # Enclose all remaining /| groupings with < >
            prereqs = re.sub("((?:[A-Za-z]|< .+ >)(?:\\s*/\\|\\s*(?:[A-Za-z]|< .+ >))+)", r"< \1 >", prereqs)
            prereqs = prereqs.replace("/|", "|")

            # Enclose all remaining , groupings with < >
            prereqs = re.sub("((?:[A-Za-z]|< [^>]+ >)(?:\\s*,\\s*(?:[A-Za-z]|< [^>]+ >))+)", r"< \1 >", prereqs)
            prereqs = prereqs.replace(",", " & ")

            # Clean spaces
            prereqs = re.sub("\\s+", " ", prereqs)

            # Remove need for "one of" since it already covered by "A or B or C" logically
            prereqs = prereqs.replace("1 ", "")

            # Encapsulate prereqs with < >
            prereqs  = "< " + prereqs.strip() + " >"

            try:
                if not len(courses):
                    prereqs = "( True )"
                else:
                    while (True):
                        new_prereqs = remove_dup_bracket(prereqs)
                        if new_prereqs == prereqs:
                            break
                        prereqs = new_prereqs

                    # Modify courses to indicate coreqs
                    courses = denote_coreqs(prereqs, courses)
                    prereqs = translate_to_python(prereqs)

                if self.logic:
                    self.logic = "( " + self.logic + " and " + prereqs + " )"
                    self.courses += courses
                    self.logic = fix_logic(self.logic)
                else:
                    self.logic = prereqs
                    self.courses = courses

            except Exception as e:
                print(e)
                print(prereqs)
                print(courses)
                self.logic = "( True )"
                self.courses = []

            self.__not_open(prereqs_alt)
            self.__students_only(prereqs_alt)
            self.__min_level(prereqs_alt)

            return True
        return False

    def __prereqs(self, prereqs):
        """
        Depreciated

        Modifies the field(s):
        prereqs
        min_grade

        :param prereqs: list(string)
        :return: None
        """
        for category in prereqs:
            if "ne of" not in category:
                category = category.split(", ")
            else:
                category = [category]

            for c in category:
                pre = []
                grades = []
                '''Cases:
                STAT 220 with a grade of at least 70%
                at least 60% in MTHEL 131
                At least 60% in ACTSC 231
                
                '''

                change = True
                match = re.findall("(?:..% (?:or higher )?in (?:one of )?)?(?:[A-Z]+ )?[1-9][0-9][0-9]" +
                                   "(?: with (?:(?:a )?(?:minimum )?grade of )?(?:at least )?..%)?", c)
                for m in match:
                    if "or" in m:
                        change = False
                    m = m.replace(" or higher", "").replace("one of ", "")
                    if m[-1] == "%":
                        grade = int(m[-3:-1])
                        course = re.search("(?:[A-Z]+ )?[1-9][0-9][0-9]", m).group()
                    elif "%" not in m:
                        course = m
                        if change:
                            grade = 50
                    else:
                        course = m[7:]
                        grade = int(m[:2])
                    pre.append(course)
                    grades.append(grade)

                if len(pre):
                    self.prereqs.append(pre)
                    self.min_grade.append(grades)

    def __not_open(self, prereqs):
        """
        Modifies the field(s):
        not_open

        :param prereqs: list(string)
        :return: None
        """
        for category in prereqs:
            m = re.search("Not open to (.*) students", category)
            if m:
                self.not_open = re.split(',| & ', m.group(1))
            m2 = re.search("Not open to students who have received credit for ([A-Z]+ [1-9][0-9][0-9])+", category)
            if m2:
                self.not_open = re.split(',| & ', m2.group(1))

    def __students_only(self, prereqs):
        """
        Modifies the field(s):
        students_only

        :param prereqs: list(string)
        :return: None
        """
        for category in prereqs:
            m = re.search("(.*) students only", category)
            if m:
                m = m.group(1).strip()
                self.students_only = re.split(" and | or ", m)
                break
            m2 = re.search("Open only to students in the following [Ff]aculties: (.*)", category)
            if m2:
                m2 = m2.group(1).strip()
                self.students_only = re.split(", | or ", m2)
                break

    def __min_level(self, prereqs):
        """
        Modifies the field(s):
        min_level

        :param prereqs: list(string)
        :return: None
        """
        for category in prereqs:
            m = re.search("Level at least ..", category)
            if m:
                self.min_level = m.group()[-2:]
                break

    def prettyprint(self, printer=True):
        output =  "Prereqs:\t\t" + str(self.prereqs) + "\n"
        output += "Min Grades:\t\t" + str(self.min_grade) + "\n"
        output += "Not open:\t\t" + str(self.not_open) + "\n"
        output += "Students only:\t" + str(self.students_only) + "\n"
        output += "Min level:\t\t" + str(self.min_level) + "\n"
        if printer:
            print(output)
        else:
            return output

    def __print_prereqs(self):
        output = ""
        for i, courses in enumerate(self.prereqs):
            for j, course in enumerate(courses):
                course = course.split()
                if len(course) == 2:
                    id = course[0]
                    num = course[1]
                else:
                    num = course[0]
                try:
                    output += id + " " + num
                except Exception as e:
                    print(courses)
                    print(course)
                    raise e

                if j != len(courses) - 1:
                    output += " or "
            if i != len(self.prereqs) - 1:
                output += ", "
        return output

    def __print_grades(self):
        output = ""
        for i, grades in enumerate(self.min_grade):
            for j, grade in enumerate(grades):
                output += str(grade)
                if i != len(self.min_grade) - 1 or j != len(grades) - 1:
                    output += ", "
        return output

    def __print_not_open(self):
        output = ""
        for i, not_open in enumerate(self.not_open):
            output += not_open.replace("'", "")
            if i != len(self.not_open) - 1:
                output += ", "
        return output

    def __print_only(self):
        output = ""
        for i, only in enumerate(self.students_only):
            output += only.replace("'", "")
            if i != len(self.students_only) - 1:
                output += ", "
        return output

    def __print_level(self):
        return self.min_level

    def str(self, flag="prereqs"):
        """
        Returns a string form of data.

        The flag field can be filled in with any of the following options:
        1. prereqs  - ex. "CS 241 or CS 245, SE 212"
        2. grades   - ex. "50, 60, 70"
        3. not_open - ex. "Software Engineering, Computer Science"
        4. only     - ex. "Computer Science"
        5. level    - ex. "3A"
        6. pretty   - prettyprint()
        7. logic    - ex. "( ( A and B ) or C )"
        8. courses  - ex. "CS 123,CS 234,CS 345"

        :param flag: string (default="prereqs")
        :return: string
        """
        output = ""
        if flag == "prereqs":
            output = self.__print_prereqs()
        if flag == "grades":
            output = self.__print_grades()
        if flag == "not_open":
            output = self.__print_not_open()
        if flag == "only":
            output = self.__print_only()
        if flag == "level":
            output = self.__print_level()
        if flag == "pretty":
            output = self.prettyprint(printer=False)
        if flag == "logic":
            output = self.logic
        if flag == "courses":
            output = ",".join(self.courses)
        return output


class Antireqs:
    def __init__(self):
        self.antireqs = []
        self.extra_info = ""

    def load_antireqs(self, antireqs):
        if isinstance(antireqs, str):
            antireqs = antireqs.replace("Antireq: ", "")
            antireqs = re.sub("[0-9]{3}[0-9]", "", antireqs)
            antireqs = re.sub("[a-zA-Z\\-]*[a-z][a-zA-Z\\-]*", "", antireqs)

            for _ in range(1):
                antireqs = re.sub("([A-Z][A-Z]+)\\s*([0-9]{3})([A-Z])\\s*/\\s*([A-Z])",
                                  r"\1 \2\3, \1 \2\4", antireqs)
                antireqs = re.sub("([A-Z][A-Z]+)\\s*([0-9]{3}[A-Z]?[A-Z]?)(?:\\s*/\\s*|\\s*,\\s*)([0-9]{3}[A-Z]?[A-Z]?)",
                                  r"\1 \2, \1 \3", antireqs)
                antireqs = re.sub("([A-Z][A-Z]+)\\s*([0-9]{3}[A-Z]?[A-Z]?)(?:\\s*/\\s*|\\s*,\\s*)"
                                  "([A-Z][A-Z]+)\\s*([0-9]{3}[A-Z]?[A-Z]?)",
                                  r"\1 \2, \3 \4", antireqs)
                antireqs = re.sub("([A-Z][A-Z]+)\\s*(?:\\s*/\\s*|\\s*,\\s*)([A-Z][A-Z]+)\\s*([0-9]{3}[A-Z]?[A-Z]?)",
                                  r"\1 \3, \2 \3", antireqs)

            self.antireqs = re.findall("(?:[A-Z]+ )?[1-9][0-9][0-9][A-Z]?[A-Z]?", antireqs)
            self.extra_info = antireqs if not len(self.antireqs) else ""
            self.__fix_antireqs()

            return True
        return False

    def __fix_antireqs(self):
        code = ""

        for i in range(len(self.antireqs)):
            antireq = self.antireqs[i]
            code_num = antireq.split()

            if len(code_num) == 2:
                code = code_num[0]
            else:
                antireq = code + " " + antireq

            self.antireqs[i] = antireq

    def str(self, flag="antireqs"):
        output = ""

        if flag == "antireqs":
            for i, antireq in enumerate(self.antireqs):
                output += antireq
                if i != len(self.antireqs) - 1:
                    output += ", "

        elif flag == "extra":
            output = self.extra_info

        return output


if __name__ == "__main__":
    p = Prereqs()
    """
    # Broken cases
    p.load_prereqs("One of (MATH 106, MATH 114, MATH 115 with a grade of at least 70%) or MATH 136 or MATH 146")
    p.load_prereqs("One of (MATH 106, MATH 115 with a grade of at least 70%) or MATH 136 and CS 135")
    p.load_prereqs("AMATH 242/CS 371 and (One of AMATH 250, 251, 350 or MATH 218, 228)")
    p.load_prereqs("BIOL 140/240 and 140/240L")
    p.load_prereqs("CHEM 120, 123 or CHEM 121, 125; Level at least 3A")
    p.load_prereqs("HLTH 101 and 102 or PSYCH 101/101R or 121R")

    # Test cases
    p.load_prereqs("Prereq: AMATH/PMATH 123")
    p.load_prereqs("CS 341, STAT 241 or at least 60% in STAT 231")
    p.load_prereqs("(One of CS 116, 136, 138, 146); MATH 136 or 146, MATH 237 or 247, STAT 231 or 241;")
    p.load_prereqs("Prereq: (CO 367 and one of CO 250, 352) or CO 255")
    p.load_prereqs("Prereq: (CO 367 and one of CO 250 or 352) or CO 255")
    p.load_prereqs("MATH 235 or 245, 237 or 247")
    p.load_prereqs("(AFM 272/ACTSC 291 or ACTSC 371 or BUS 393W or ECON 371) and"
                   " (CO 227 or CO 250 with a grade of at least 70% or CO 255 or CO 352).")"""
    """
    p.load_prereqs("FINE 319; At least four 200-level FINE studio courses; Level at least 3A")
    p.load_prereqs("At least 1.0 unit of 300-level FINE studio courses")
    p.load_prereqs("Open only to students in the following faculties: ARTS, AHS or ENV.")
    p.load_prereqs("Coreq: FINE 474.")
    p.load_prereqs("At least 70% in one of EMLS 101R, 102R, EMLS/ENGL 129R, ENGL 109, SPCOM 100, 223;"
                   "one of STAT 331, 371, ACTSC 331; Actuarial Science/CFM or Statistics major students")
    p.load_prereqs("One of BME 411, CIVE 332, CO 250, ENVE 320/335, MSCI 331, or SYDE 411; "
                   "Level at least 3B Management Engineering or MSCI Option.")
    p.load_prereqs("(At least 60% in ACTSC 231) and (STAT 230 or 240) and (at least 60% in MTHEL 131). "
                   "Not open to students who received credit for ACTSC 331.")
    p.load_prereqs("(AFM 372/ACTSC 391or(ACTSC 231, 371)or(ACTSC 231, BUS 393W)),((STAT 330,333) or STAT 334);"
                   " ACTSC, Math/FARM, Math Fin students only.")
    p.load_prereqs("3A Systems Design Engineering or (MATH 115 and MTE 202 and"
                   " level at least 3A Mechatronics Engineering)")
    p.load_prereqs("(For Mathematics students) one of EMLS 101R, 102R, EMLS/ENGL 129R, ENGL 109, SPCOM 100, SPCOM 223")
    p.load_prereqs("Fourth Year Health Studies")
    p.load_prereqs("AMATH 242/CS 371 and (One of AMATH 250, 251, 350 or MATH 218, 228)")
    p.load_prereqs("MATH 237 or 247 and (Two of AMATH 250 or 251, MATH 211/ECE 205, MATH 218, 228); Level at least 3B")
    p.load_prereqs("MATH 136 or 146, 237 or 247, STAT 230or240 &(one of AFM 272/ACTSC 291,ACTSC 371,ECON 371,BUS 393W);"
                   "Lev at least 3A;Not open to GenMath stdts.")
    p.load_prereqs("Level at least 3A and ENGL 335")
    p.load_prereqs("ECON101 or ECON100/COMM103;ECON211 or one of MATH128,138,148; ECON221 or one of ARTS280,ENVS278,"
                   "KIN222,232,PSCI214/314,PSYCH292, SWREN250R; or Math/FARM stdnts.")
    p.load_prereqs("One of CS 135, 145 or MATH 135, 145")
    p.load_prereqs("One of ECON 221, ENVS 278, HLTH 204, SDS 250R, KIN 232, PSCI 214/314, PSYCH 292,"
                   " REC 371, SOC/LS 280, any STAT course;")
    p.load_prereqs("BIOL 273 or BME 284 or SYDE 384/584; Level at least 3A Biomedical Engineering or Level at least 3B "
                   "Systems Design Engineering or Level at least 3B Honours Life Physics (Biophysics Specialization)")
    p.load_prereqs("(MATH 135 with a grade of at least 60% or MATH 145; Honours Mathematics or Mathematics/ELAS"
                   " students) or Science Mathematical Physics students.")
    p.load_prereqs("CS 240, (CS 246 or 247);PD 10; Software Engineering")
    p.load_prereqs("CHEM 262L (for Chemical Engineering students only).")
    p.load_prereqs("Level at least 1B Mechatronics Engineering, CHE 102.")
    p.load_prereqs("BIOL 110, 120, 150/250 or ENVS 200, STAT 202, or ENVS 278")
    p.load_prereqs("Cumulative Major Average at least 73%; Honours Biology, Biochemistry, Biomedical Sciences, "
                   "Environmental Science - Ecology Specialization, Life Physics - Biophysics Specialization only.")
    p.load_prereqs("BIOL 308 or 309 and CHEM 233 or 237; BIOL 308 or BIOL 309 and co-req CHEM 233 or CHEM 237 for"
                   " Science and Business/Biotechnology Specialization or Honours Biotechnology/Economics or CS "
                   "Honours Bioinformatics")
    p.load_prereqs("(CS 138 or 246) or (a grade of 85% or higher in one of CS 136 or 146); Computer Science and BMath "
                   "(Data Science) students only.")
    p.load_prereqs("MATH 137 or 147 and (STAT 220 with a grade of at least 70% or a corequisite of STAT 230 or 240); "
                   "Level at least 2A; Not open to students who have received credit for ACTSC 232.")"""
    """
    # Broken Cases
    # p.load_prereqs("BIOL 140/240 and 140/240L")  # BIOL [fixed]
    # p.load_prereqs("PSYCH 101/101R")  # PSYCH [not broken]
    p.load_prereqs("BIOL 308 or 309 and CHEM 233 or 237; BIOL 308 or BIOL 309 and co-req CHEM 233 or CHEM 237 for"
                   " Science and Business/Biotechnology Specialization or Honours Biotechnology/Economics or CS "
                   "Honours Bioinformatics")  # BIOL
    #p.load_prereqs("SPCOM 101 or for Mathematics students one of EMLS 101R, EMLS 102R, EMLS/ENGL 129R, ENGL 109, "
    #               "SPCOM 100, SPCOM 223; Level at least 2A")  # SPCOM
    # p.load_prereqs("1.0 unit of PSYCH; Level at least 3A")  # PSYCH [fixed]
    # p.load_prereqs("PSYCH 354/354R or (PSYCH 253A/253B and SMF 306);")  # PSYCH [fixed]
    # p.load_prereqs("HLTH 101 and 102 or PSYCH 101/101R or 121R")  # HLTH [fixed]
    # p.load_prereqs("A grade of 85% or higher in one of CS 136, 138 or 146; "
    #                "Computer Science students only.")  # CS [fixed]
    # p.load_prereqs("One of ECON 221, ENVS 278, HLTH 204, SDS 250R, KIN 232, PSCI 214/314, PSYCH 292, REC 371, "
    #                "SOC/LS 280, any STAT course;")  # STAT [not broken]
    # p.load_prereqs("(ECE 105, 106) or (PHYS 112 or 122); (ECE 205 or MATH 211) or ((MATH 227 or 237 or 247) "
    #                "and (MATH 228 or AMATH 250 or 251)).")  # ECE [fixed]
    # p.load_prereqs("(One of PHYS 112, 122) or (ECE 105, 106); (One of MATH 108, 119, 128, 138, 148).")  # ECE [fixed]
    p.load_prereqs("(Level at least 4A Computer Engineering or Electrical Engineering) or (MATH 213, STAT 206; "
                   "Level at least 3B Software Engineering)")  # ECE
    # p.load_prereqs("0.50 units in PHIL")  # PHIL [fixed]
    p.load_prereqs("FINE 308; At least 1.0 unit in 300-level FINE studio courses; a grade of 75% in each 300-level"
                   " studio course; Level at least 4A Intensive Studio Specialization.")  # FINE
    p.load_prereqs("475.", "FINE")  # FINE
    # p.load_prereqs("PHYS 234 or CHEM 356;One of MATH 228,AMATH 250,251; MATH 227 or 237 or 247.")  # PHYS [not broken]
    p.load_prereqs("PHYS 256L for Science students except for Mathematical Physics Plan.")  # PHYS
    # p.load_prereqs("One of PHYS 122 (winter 2019 or later), 224, 242")  # PHYS [fixed]
    # p.load_prereqs("One of PHYS 112, 122, 125, ECE 106; One of MATH 128, 138, 148,(SYDE 111,112);One of PHYS 224, 233,"
    #                " CS 473, CHEM 209, 356; Level at least 3A SCI, MATH or ENG stdnts")  # PHYS [partially fixed]
    p.load_prereqs("One of MATH 128, 138, 148,(SYDE 111,112);")"""
    # p.load_prereqs("(PHYS 334 or AMATH 373); PHYS 363; (PHYS 364 and 365) or (AMATH 332, 351, 353)") [fixed]
    #p.load_prereqs("Level at least 4A; one of PHYS 380, 383, 395, 396")  # PHYS [not broken]
    """p.load_prereqs("ECON 211 or Science and Business students or Biotech/Chartered Professional"
                   " Accountancy students.")  # ECON
    p.load_prereqs("ECON101 or ECON100/COMM103;ECON211 or one of MATH128,138,148; ECON221 or one of ARTS280,ENVS278,"
                   "KIN222,232,PSCI214/314,PSYCH292, REC371, SDS250R, SMF230, SOC/LS280,STAT202, 206,211,220,230,240,"
                   " SWREN250R; or Math/FARM stdnts.")  # ECON
    p.load_prereqs("ECON 201, 202, ECON 211; or ECON 391; Not open to students in the Faculty of Mathematics")  # ECON
    p.load_prereqs("ECON 221; or for Mathematics students ECON 101, 102 or ECON 100/COMM 103 and one of STAT 220, "
                   "230, 240; or for Accounting students ECON 101, 102, STAT 211.")  # ECON
    p.load_prereqs("ECON 201, 202 or ECON 201, 206 or ECON 206, 290.")  # ECON
    p.load_prereqs("ECON371; ECON211 or one of MATH106/136/146; ECON 221 or any probability and/or basic"
                   " statistics course; or for Math stdnts ECON101 or ECON100/COMM103, ECON102 and ACTSC372"
                   " after fall 2014.")  # ECON
    p.load_prereqs("FINE 319; At least four 200-level FINE studio courses; Level at least 3A")
    p.load_prereqs("At least 1.0 unit of 300-level FINE studio courses")"""
    # p.load_prereqs("One of ECON 221, STAT 211, 231, 241; AFM 241 or CS 330; Accounting and Financial Management, "
    #                "Mathematics/CPA, or Biotechnology/CPA students.")  # AFM
    # p.load_prereqs("CHEM 262 or 264 or 266 or NE 122/222.")  # CHEM
    # p.load_prereqs("CHEM 233 or 237 or NE 224 and CHEM 265 or 267.")  # CHEM
    # p.load_prereqs("MATH 136 or 146, 237 or 247, STAT 230or240 &(one of AFM 272/ACTSC 291,ACTSC 371,ECON 371,BUS 393W);"
    #                "Lev at least 3A;Not open to GenMath stdts.")
    # p.load_prereqs("(AFM 372/ACTSC 391or(ACTSC 231, 371)or(ACTSC 231, BUS 393W)),((STAT 330,333) or STAT 334); ACTSC,"
    #                " Math/FARM, Math Fin students only.")
    # p.load_prereqs("CS 341, STAT 241 or at least 60% in STAT 231")
    # p.load_prereqs("CHEM 123 or 125, MATH 128;")
    # p.load_prereqs("CHEM 120, 123 or CHEM 121, 125;")
    p.load_prereqs("One of PHYS 112,122; Two of MATH 128, 138, 148; (MATH 227 or co-requisite: AMATH 231).")  # PHYS
    p.load_prereqs("MATH 137 or 147 and (STAT 220 with a grade of at least 70% or a corequisite of STAT 230 or 240); "
                   "Level at least 2A; Not open to students who have received credit for ACTSC 232.")  # ACTSC
    p.load_prereqs("Prereq: MATH 145 or")
    p.load_prereqs("Coreq: MATH 136")
    p.load_prereqs("One of MATH 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, CS 100, 101, 102, 103, 104, 105, 106"
                   ", 107, 108, 109, STAT 100, 101, 102, 103, 104, 105, 106, 107, 108, 109")
