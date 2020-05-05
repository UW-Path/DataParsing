"""
DatabaseReceiver.py receives information about UW courses from SQL database.

Contributors:
Calder Lund
"""

from Database.DatabaseConnection import DatabaseConnection
import pandas as pd

# Might not need in the future (Hao Wei 2020/01/09)

class DatabaseReceiver(DatabaseConnection):
    def __init__(self):
        DatabaseConnection.__init__(self)

    def get_course_info(self, condition = ""):
        """
        Calls DatabaseConnection.select to retrieve data from course info table.

        :return: pandas.DataFrame
        """
        columns = ["index", "course_code", "course_id", "course_name", "credit", "info", "offering",
                   "online", "prereqs", "coreqs", "antireqs"]
        data = self.select("*", self.course_table, condition)
        df = pd.DataFrame(data, columns=columns)
        df.set_index("index", inplace=True)
        return df

    def get_prereqs(self, condition = ""):
        """
        Calls DatabaseConnection.select to retrieve data from prereqs table.

        :return: pandas.DataFrame
        """
        columns = ["index", "course_code", "logic", "courses", "grades", "not_open", "only_from", "min_level"]
        data = self.select("*", self.prereqs_table, condition)
        df = pd.DataFrame(data, columns=columns)
        df.set_index("index", inplace=True)
        return df

    def get_antireqs(self, condition = ""):
        """
        Calls DatabaseConnection.select to retrieve data from antireqs table.

        :return: pandas.DataFrame
        """
        columns = ["index", "course_code", "antireq", "extra_info"]
        data = self.select("*", self.antireqs_table, condition)
        df = pd.DataFrame(data, columns=columns)
        df.set_index("index", inplace=True)
        return df
