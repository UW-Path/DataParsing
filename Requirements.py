"""
Requirements is an object class that parses and tracks information
pertaining to prerequisites and anti-requisites.

Date:
October 13th, 2019

Contributors:
Calder Lund
"""

import re


class Prereqs:
    def __init__(self):
        self.prereqs = []
        self.min_grade = []  # Parallel list to prereqs
        self.not_open = []
        self.students_only = []
        self.min_level = "1A"

    def load_prereqs(self, prereqs):
        """
        Parses the necessary prerequisite data.

        :param prereqs: string
        :return: boolean
        """
        if isinstance(prereqs, str):
            prereqs = prereqs.replace("Prereq: ", "")
            prereqs_alt = re.split(";|\\.", prereqs)
            prereqs = re.split(";|\\.|\\), |and", prereqs)
            prereqs = [prereq for prereq in prereqs if prereq]

            self.__prereqs(prereqs)  # sets prereqs and min_grade
            self.__not_open(prereqs_alt)
            self.__students_only(prereqs_alt)
            self.__min_level(prereqs_alt)

            return True
        return False

    def __prereqs(self, prereqs):
        """
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
                # at least XX% in CS XXX
                change = True
                match = re.findall("(?:..% (?:or higher )?in (?:one of )?)?(?:[A-Z]+ )?[1-9][0-9][0-9]" +
                                   "(?: with a grade of at least ..%)?", c)
                for m in match:
                    if "or" in m:
                        change = False
                    m = m.replace(" or higher", "").replace("one of ", "")
                    if m[-1] == "%":
                        grade = m [-3:-1]
                        course = m[:-3].replace(" with a grade of at least ", "")
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
                break

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
                self.students_only = re.split(" and ", m)
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
                output += id + " " + num
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
            output += not_open
            if i != len(self.not_open) - 1:
                output += ", "
        return output

    def __print_only(self):
        output = ""
        for i, only in enumerate(self.students_only):
            output += only
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
        return output
