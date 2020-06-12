"""
Major is an object class that stores information for major requirements

Contributors:
Hao Wei Huang
"""

import re
from StringToNumber import StringToNumber


class MajorReq:
    def __init__(self, list, req, program, relatedMajor, additionalRequirement, additional = 0):
        self.list = list
        self.programName = program
        self.majorName = relatedMajor  # self._get_related(relatedMajor)
        self.req = req
        self.planType = self.__plan_type()
        self.additional = additional
        self.courseCodes = self.__course_codes()
        self.numberOfCourses = self.__number_of_courses()
        self.additionalRequirement = additionalRequirement
        self.credits = 0.5

    def __has_numbers(self, input_string):
        """
                Check if input_string has numbers (0-9)
                :return: bool
        """
        return bool(re.search(r'\d', input_string))

    def __require(self):
        """
                Return course appended together (for one of)
                Note: Append list at the end with comma
                :return: str
        """
        return ", ".join(self.list)

    def __course_codes(self):
        """
        Returns course code of a block of requirement (either One of/All of/Additional)

        :return: string
        """
        return self.__require()

    def __number_of_courses(self):
        """
                Returns courses needed for the group of course_codes

                :return: int
        """
        pass

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
        elif "table" in str(self.programName).lower():
            return "Table"
        else:
            # Assume it is major
            return "Major"

    def __str__(self):
        pass
