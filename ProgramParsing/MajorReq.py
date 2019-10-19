"""
Major is an object class that stores information for major requirements

Date:
October 14th, 2019

Contributors:
Hao Wei Huang
"""

import re


class MajorReq:
    def __init__(self, html, type, major, additional = 0):
        self.html = html
        self.major = major
        self.type = type
        self.additional = additional
        self.courseCode = self.__course_code()
        self.numberOfCourses = self.__number_of_courses()

    def __has_numbers(self, input_string):
        return bool(re.search(r'\d', input_string))

    def __require_all(self):
        # hold be parsed already by course parser
        return self.html.contents[0]

    def __require_one(self):
        vals = []
        courses = self.html.findAll("a")
        for course in courses:
            vals.append(course.contents[0])
        return ", ".join(vals)

    def __additional(self):
        vals = []
        if self.html.name == "blockquote":
            for line in self.html.contents:
                if line.name == "a" and self.__has_numbers(line.contents[0]):
                    vals.append(line.contents[0])
                else:
                    match = re.findall(r"[A-Z]+\s{0,1}[1-9][0-9][0-9]\s{0,1}-\s{0,1}[A-Z]+\s{0,1}[1-9][0-9][0-9]",
                                       str(line))
                    if match:
                        for m in match:
                            course = m.strip("\n")
                            vals.append(course)
        else:
            match = re.findall(r"[A-Z]+\s{0,1}[1-9][0-9][0-9]\s{0,1}-\s{0,1}[A-Z]+\s{0,1}[1-9][0-9][0-9]",
                               str(self.html.contents[0]))
            if match:
                for m in match:
                    course = m.strip("\n")
                    vals.append(course)

        return ", ".join(vals)

    def __course_code(self):
        """
        Returns course code of a block of requirement (either One of/All of)

        :return: string
        """
        if self.type == "One of":
            return self.__require_one()
        elif self.type == "All of":
            return self.__require_all()
        elif self.type == "Additional":
            return self.__additional()

    def __number_of_courses(self):
        if self.type == "One of":
            return 1
        elif self.type == "All of":
            return 1
        elif self.type == "Additional":
            return self.additional

    def __str__(self):
        output = "Requirement for: " + self.major
        output += "\n"
        if self.type == "Additional":
            output += "\tCourse (" + self.type + " " + str(self.additional) + " of) : " + self.courseCode + "\n"
        else:
            output += "\tCourse (" + self.type + ") : " + self.courseCode + "\n"
        return output
