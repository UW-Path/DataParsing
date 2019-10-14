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
            prereqs = re.split(";|\.", prereqs)

            self.__prereqs(prereqs)  # sets prereqs and min_grade
            self.__not_open(prereqs)
            self.__students_only(prereqs)
            self.__min_level(prereqs)

            return True
        return False

    def __prereqs(self, prereqs):
        for category in prereqs:
            # at least XX% in CS XXX
            m = re.findall("[aA]t least ..% in [A-Z]+ [1-9][0-9][0-9]", category)
            for minimum in m:
                course = minimum[16:]
                grade = int(minimum[9:11])
                self.prereqs.append(course)
                self.min_grade.append(grade)

            # CS XXX with a grade of at least XX%
            m = re.findall("[A-Z]+ [1-9][0-9][0-9] with a grade of at least ..%", category)
            for minimum in m:
                course = minimum[:-29]
                grade = int(minimum[-3:-1])
                self.prereqs.append(course)
                self.min_grade.append(grade)

            # A grade of XX% or higher in CS XXX, YYY, or SE ZZZ
            m = re.findall("[aA] grade of ..% or higher in(?: one of)? (?:(?:[A-Z]+ )?[1-9][0-9][0-9](?:, or |, | or )?)+", category)
            for mini in m:
                mini = mini.replace(" one of", "")
                courses = re.split(", or |, | or ", mini[28:])
                grade = int(mini[11:13])
                for course in courses:
                    self.prereqs.append(course)
                    self.min_grade.append(grade)

            # TODO - add functionality for other texts

    def __not_open(self, prereqs):
        for category in prereqs:
            m = re.search("Not open to (.*) students", category)
            if m:
                self.not_open = re.split(',| & ', m.group(1))
                break

    def __students_only(self, prereqs):
        for category in prereqs:
            m = re.search("(.*) students only", category)
            if m:
                m = m.group(1).strip()
                self.students_only = re.split(" and ", m)
                break

    def __min_level(self, prereqs):
        for category in prereqs:
            m = re.search("Level at least ..", category)
            if m:
                self.min_level = m.group()[-2:]
                break
