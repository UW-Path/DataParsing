"""
Major is an object class that stores information for major requirements

Date:
October 14th, 2019

Contributors:
Hao Wei Huang
"""

import re


class MajorReq:
    def __init__(self, html, req, program, additional = 0):
        self.html = html
        self.programName = program
        self.req = req
        self.planType = self.__plan_type()
        self.additional = additional
        self.courseCodes = self.__course_codes()
        self.numberOfCourses = self.__number_of_courses()
        #TODO: Require Table II

    def __has_numbers(self, input_string):
        """
                Check if input_string has numbers (0-9)
                :return: bool
        """
        return bool(re.search(r'\d', input_string))

    def __require_all(self):
        """
                Return course (for ALL courses)
                :return: str
        """
        # hold be parsed already by course parser
        return self.html.contents[0]

    def __require(self):
        """
                Return course appended together (for one of)
                Note: Append list at the end with comma
                :return: str
        """
        vals = []
        courses = self.html.findAll("a")
        for course in courses:
            vals.append(course.contents[0])
        return ", ".join(vals)

    def __additional(self):
        """
                Return course (for Additional courses)
                Note: Append list at the end with comma
                :return: str
        """
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

            #loop through to find all string
            i = 0
            while(i < len(self.html.contents)):
                match = re.findall(r"[A-Z]+\s{0,1}[1-9][0-9][0-9]\s{0,1}-\s{0,1}[A-Z]+\s{0,1}[1-9][0-9][0-9]",
                                   str(self.html.contents[i]))
                if match:
                    for m in match:
                        course = m.strip("\n")
                        vals.append(course)
                i+=1
            #serach for links
            match = self.html.find_all("a")
            if (match):
                for course in match:
                    vals.append(course.string)
                #TODO : FILL IT IN

        return ", ".join(vals)

    def __course_codes(self):
        """
        Returns course code of a block of requirement (either One of/All of/Additional)

        :return: string
        """

        if self.req == "All of":
            return self.__require_all()
        elif self.req == "Additional":
            return self.__additional()
        else:
            return self.__require()

    def __number_of_courses(self):
        """
                Returns courses needed for the group of course_codes

                :return: int
        """
        if self.req == "One of":
            return 1
        elif self.req == "All of":
            return 1
        elif self.req == "Two of":
            return 2
        elif self.req == "Three of":
            return 3
        elif self.req == "Four of":
            return 4
        elif self.req == "Additional":
            return self.additional

    def __plan_type(self):
        """
                Returns the type of plan (Major, Minor, Specialization, Optimization)
                :return: int
        """
        if "joint" in str(self.programName).lower():
            return "Joint"
        elif "minor" in str(self.programName).lower():
            return "Minor"
        elif "specialization" in str(self.programName).lower():
            return "Specialization"
        elif "option" in str(self.programName).lower():
            return "Option"
        else:
            # Assume it is major
            return "Major"

    def __str__(self):
        output = "Requirement for: " + self.programName + " (" + self.planType + ")"
        output += "\n"
        if self.req == "Additional":
            output += "\tCourse (" + self.req + " " + str(self.additional) + ") : " + self.courseCodes + "\n"
        else:
            output += "\tCourse (" + self.req + ") : " + self.courseCodes + "\n"
        return output
