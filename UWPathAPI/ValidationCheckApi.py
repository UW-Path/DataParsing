"""
ValidationCheckApi.py is a controller to validate if course can be taken

Contributors:
Hao Wei Huang

Last Updated Dec 8
"""

class ValidationCheckApi:
    def __init__(self, connection):
        self.dbc = connection

    def get_course_anti_reqs(self, course_name):
        """
        return all anti-reqs of a given course

        :param course_name: str
        :return: list of str
        """
        condition = "WHERE COURSE_CODE = '" + course_name + "' "
        anti_reqs = self.dbc.get_antireqs(condition)
        if (not anti_reqs.empty):
            anti_reqs = anti_reqs.iloc[0]["antireq"].split(",")
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
            co_reqs = co_reqs.iloc[0]["coreq"].split(",")
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
            prereq = prereq.iloc[0]["prereq"].split(",")
        else:
            prereq = []
        return prereq