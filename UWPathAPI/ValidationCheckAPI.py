"""
ValidationCheckAPI.py is a controller to validate if course can be taken

Contributors:
Hao Wei Huang

Last Updated Dec 8
"""

from builtins import any

class ValidationCheckAPI:
    def __init__(self, connection):
        self.dbc = connection

    def can_take_course(self, list_of_courses_taken, course):
        #TODO Throw errors in the future
        """
        Check if the course violates any prereq, coreq, and antireq requirments (ignore coreqs for now)
        :param list_of_courses_taken: list[str]
        :param course: str
        :return: Bool
        """
        anti_reqs = self.get_course_anti_reqs(course)
        pre_reqs = self.get_course_pre_reqs(course)

        #ex: antireqs = [MATH 128, MATH 129] we want to check if
        for anti_req in anti_reqs:
            if(any(c in anti_req for c in list_of_courses_taken)):
                return False

        for pre_req in pre_reqs:
            met_req = False
            pre_req = pre_req.split(" or ")
            #seperate or in one pre-req string
            for p in pre_req:
                if p in list_of_courses_taken:
                    met_req = True
                    break
            if not met_req:
                return False
        return True



    def get_course_anti_reqs(self, course_name):
        """
        return all anti-reqs of a given course

        :param course_name: str
        :return: list of str
        """
        condition = "WHERE COURSE_CODE = '" + course_name + "' "
        anti_reqs = self.dbc.get_antireqs(condition)
        if (not anti_reqs.empty):
            anti_reqs = anti_reqs.iloc[0]["antireq"].split(", ")
        else:
            anti_reqs = []
        return anti_reqs

    def get_course_co_reqs(self, course_name):
        """
        return all coreqs of a given course

        :param course_name: str
        :return: list of str with "or" statements in some
        """
        condition = "WHERE COURSE_CODE = '" + course_name + "' "
        co_reqs = self.dbc.get_coreqs(condition)
        if (not co_reqs.empty):
            co_reqs = co_reqs.iloc[0]["coreq"].split(", ")
        else:
            co_reqs = []
        return co_reqs

    def get_course_pre_reqs(self, course_name):
        """
        return all prereqs of a given course

        :param course_name: str
        :return: list of str with "or" statements in some
        """
        condition = "WHERE COURSE_CODE = '" + course_name + "' "
        prereq = self.dbc.get_prereqs(condition)
        if (not prereq.empty):
            prereq = prereq.iloc[0]["prereq"].split(", ")
        else:
            prereq = []
        return prereq