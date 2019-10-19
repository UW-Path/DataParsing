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
        self.courseCode = self.__courseCode() # course code
        self.numberOfCourses = self.__numberOfCourses()

    def __hasNumbers(self, inputString):
        return bool(re.search(r'\d', inputString))

    def __requireAll(self):
        #shold be parsed already by courseparser
        return self.html.contents[0]

    def __requireOne(self):
        list = []
        courses = self.html.findAll("a")
        for course in courses:
            list.append(course.contents[0])
        return ", ".join(list)

    def __additional(self):
        list = []
        if self.html.name == "blockquote":
            for line in self.html.contents:
                if line.name == "a" and self.__hasNumbers(line.contents[0]):
                    list.append(line.contents[0])
                else:
                    match = re.findall(r"[A-Z]+\s{0,1}[1-9][0-9][0-9]\s{0,1}-\s{0,1}[A-Z]+\s{0,1}[1-9][0-9][0-9]",
                                       str(line))
                    if(match):
                        for m in match:
                            course = m.strip("\n")
                            list.append(course)
        else:
            match = re.findall(r"[A-Z]+\s{0,1}[1-9][0-9][0-9]\s{0,1}-\s{0,1}[A-Z]+\s{0,1}[1-9][0-9][0-9]", str(self.html.contents[0]))
            if (match):
                for m in match:
                    course = m.strip("\n")
                    list.append(course)

        return ", ".join(list)

    def __courseCode(self):
        """
        Returns course code of a block of requirement (either One of/All of)

        :return: string
        """
        if self.type == "One of":
            return self.__requireOne()
        elif self.type == "All of":
            return self.__requireAll()
        elif self.type == "Additional":
            return self.__additional()


    def __numberOfCourses(self):
        if self.type == "One of":
            return 1
        elif self.type == "All of":
            return 1
        elif self.type == "Additional":
            return self.additional



    def __str__(self):
        output =  "Requirement for: " + self.major
        output += "\n"
        if (self.type == "Additional"):
            output += "\tCourse (" + self.type + " " + str(self.additional) + " of) : " + self.courseCode + "\n"
        else:
            output += "\tCourse (" + self.type + ") : " + self.courseCode + "\n"
        return output