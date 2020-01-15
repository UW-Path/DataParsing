"""
ValidationCheckAPI.py is a controller to validate if course can be taken

Contributors:
Hao Wei Huang
Calder Lund

Last Updated Jan 12th
"""

from builtins import any


class ValidationCheckAPI:
    def __init__(self):
        self.antireqs = []
        self.prereqs = []
        self.coreqs = []

    def set_antireqs(self, antireqs):
        """
        Sets all anti-reqs of a given course.

        :param antireqs: str
        """
        if len(antireqs):
            self.antireqs = antireqs.split(", ")
        else:
            self.antireqs = []

    def set_coreqs(self, coreqs):
        """
        Sets all coreqs of a given course.

        :param coreqs: str
        """
        if len(coreqs):
            self.coreqs = coreqs.split(", ")
        else:
            self.coreqs = []

    def set_prereqs(self, prereqs):
        """
        Sets all prereqs of a given course.

        :param prereqs: str
        """
        if len(prereqs):
            self.prereqs = prereqs.split(", ")
        else:
            self.prereqs = []

    def can_take_course(self, list_of_courses_taken, current_term_courses, course):
        # TODO Throw errors in the future
        """
        Check if the course violates any prereq, coreq, and antireq requirments
        :param list_of_courses_taken: list[str]
        :param course: str
        :return: Bool
        """

        # ex: antireqs = [MATH 128, MATH 129] we want to check if
        for anti_req in self.antireqs:
            if any(c in anti_req for c in list_of_courses_taken):
                return False

        for co_req in self.coreqs:
            met_req = False
            co_req = co_req.split(" or ")
            # separate or in one co_req string
            for c in co_req:
                if c in current_term_courses or c in list_of_courses_taken:
                    met_req = True
                    break
            if not met_req:
                return False

        for pre_req in self.prereqs:
            met_req = False
            pre_req = pre_req.split(" or ")
            # separate or in one pre-req string
            for p in pre_req:
                if p in list_of_courses_taken:
                    met_req = True
                    break
            if not met_req:
                return False
        return True
