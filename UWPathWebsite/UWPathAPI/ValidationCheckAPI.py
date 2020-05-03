"""
ValidationCheckAPI.py is a controller to validate if course can be taken

Contributors:
Hao Wei Huang
Calder Lund

Last Updated Jan 12th
"""

from builtins import any


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

    def can_take_course(self, list_of_courses_taken, current_term_courses, course):
        # TODO Throw errors in the future
        """
        Check if the course violates any prereq, coreq, and antireq requirments
        :param list_of_courses_taken: list[str]
        :param course: str
        :return: Bool
        """

        # ANTIREQ
        for anti_req in self.antireqs:
            if any(c in anti_req for c in list_of_courses_taken + current_term_courses):
                return False

        # PREREQ & COREQ
        prereq_logic = self.prereq_logic
        for i in range(len(self.prereq_courses)):
            if self.prereq_courses[i][0] == "_":
                if self.prereq_courses[i][1:] in list_of_courses_taken + current_term_courses:
                    prereq_logic = prereq_logic.replace(get_char(i)+" ", "True ")
                else:
                    prereq_logic = prereq_logic.replace(get_char(i)+" ", "False ")
            else:
                if self.prereq_courses[i] in list_of_courses_taken:
                    prereq_logic = prereq_logic.replace(get_char(i)+" ", "True ")
                else:
                    prereq_logic = prereq_logic.replace(get_char(i)+" ", "False ")

        try:
            return eval(prereq_logic)
        except Exception as e:
            # EMAIL(course, self.prereq_courses, self.prereq_logic, list_of_courses_taken, current_term_courses, e)
            return True
