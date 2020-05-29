"""
ValidationCheckAPI.py is a controller to validate if course can be taken

Contributors:
Hao Wei Huang
Calder Lund

Last Updated Jan 12th
"""

from builtins import any
from datetime import datetime

from django.core.mail import EmailMessage

from django_projects import settings

import re


def get_char(i):
    if i + ord('A') > ord('Z'):
        return chr(i - 26 + ord('a'))
    return chr(i + ord('A'))

def get_index(c):
    if ord(c) - ord('A') > 26:
        return ord(c) - ord('a') + 26
    return ord(c) - ord('A')


class ValidationCheckAPI:
    def __init__(self):
        self.antireqs = []
        self.prereq_logic = ""
        self.prereq_courses = []
        self.coreq_logic = ""
        self.coreq_courses = []

    def set_antireqs(self, antireqs):
        """
        Sets all anti-reqs of a given course.

        :param antireqs: str
        """
        if len(antireqs):
            self.antireqs = antireqs.split(", ")
        else:
            self.antireqs = []

    def set_coreqs(self, logic, courses):
        """
        Sets all coreqs of a given course.

        :param coreqs: str
        """
        if len(logic):
            self.coreq_logic = logic
        else:
            self.coreq_logic = "True"
        if len(courses):
            self.coreq_courses = courses.split(",")
        else:
            self.coreq_courses = []

    def set_prereqs(self, logic, courses):
        """
        Sets all prereqs of a given course.

        :param prereqs: str
        """
        if len(logic):
            self.prereq_logic = logic
        else:
            self.prereq_logic = "True"
        if len(courses):
            self.prereq_courses = courses.split(",")
        else:
            self.prereq_courses = []

    def level_can_take(self, logic, course, taken_courses, i):
        if course.endswith("000"):
            print(logic.find(get_char(i)))
            new_string = ""
            for taken in taken_courses:
                course_start = re.match("[A-Z]+ [1-9]", taken).group(0)
                if course_start == course[:-3]:
                    new_string += "True and "
            if new_string == "":
                logic = logic.replace(get_char(i)+" ", "False ")
            else:
                logic = logic.replace(get_char(i)+" ", new_string[:-5]+" ")
            print(logic)
        elif course in taken_courses:
            logic = logic.replace(get_char(i)+" ", "True ")
        else:
            logic = logic.replace(get_char(i)+" ", "False ")

        iter = re.finditer("len\\(tuple\\(filter\\(None,\\[ (?:True|False)((?: and True)+)", logic)
        for m in iter:
            start = m.start(0)
            end = m.end(0)
            logic = logic[:start] + logic[start:end].replace(" and", ",") + logic[end:]

        return logic

    def can_take_course(self, list_of_courses_taken, current_term_courses, course):
        # TODO Throw errors in the future
        """
        Check if the course violates any prereq, coreq, and antireq requirments
        :param list_of_courses_taken: list[str]
        :param course: str
        :return: Bool
        """
        print(list_of_courses_taken)

        # ANTIREQ
        for anti_req in self.antireqs:
            if any(c in anti_req for c in list_of_courses_taken + current_term_courses):
                return False

        # Course cannot be repeated
        if course in list_of_courses_taken:
            return False

        # PREREQ & COREQ
        prereq_logic = self.prereq_logic
        for i in range(len(self.prereq_courses)):
            if self.prereq_courses[i][0] == "_":
                prereq_logic = self.level_can_take(prereq_logic, self.prereq_courses[i][1:],
                                                   list_of_courses_taken + current_term_courses, i)
            else:
                prereq_logic = self.level_can_take(prereq_logic, self.prereq_courses[i],
                                                   list_of_courses_taken, i)

        try:
            return eval(prereq_logic)
        except Exception as e:
            # EMAIL(course, self.prereq_courses, self.prereq_logic, list_of_courses_taken, current_term_courses, e)
            # Error Log
            # TODO: Prevent sending multiple emails with the same error in a short amount of time
            error_message = "Error Message: " + str(e) + "."
            error_message += "\n\ncan_take_course({}, {}, {})".format(list_of_courses_taken, current_term_courses, course)
            error_message += "\n\nOccurred at: " + str(datetime.now()) + " (UTC)"
            msg = EmailMessage("Error in ValidationCheckAPI/CanTakeCourse",
                               error_message,
                               settings.EMAIL_HOST_USER,
                               [settings.EMAIL_HOST_USER])
            msg.send()
            return True
