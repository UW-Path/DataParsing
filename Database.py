"""
Database.py receives information about UW courses and sends that information
to an SQL database for later use.

Date:
October 13th, 2019

Updated:
October 19th, 2019

Contributors:
Calder Lund
Hao Wei Huang
"""

import psycopg2
import logging
import sys

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


class DatabaseConnection:
    def __init__(self, user="postgres", password="1234", host="localhost", port="8888", database="postgres",
                 course_table="course_info", prereqs_table="prereqs", antireqs_table="antireqs"):
        self.connection = psycopg2.connect(user=user, password=password, host=host, port=port, database=database)
        self.cursor = self.connection.cursor()
        self.course_table = course_table
        self.prereqs_table = prereqs_table
        self.antireas_table = antireqs_table

    def execute(self, command):
        try:
            root.info(command)
            self.cursor.execute(command)
            return True
        except Exception as e:
            root.error(e)
            return False

    def commit(self):
        if self.connection:
            self.connection.commit()

    def close(self):
        self.connection.close()

    def create_courses(self):
        """
        Creates courses table.
        """
        # TODO - remove antireq field
        command = "CREATE TABLE IF NOT EXISTS " + self.course_table + """ (
            id SERIAL PRIMARY KEY,
            course_code VARCHAR(255),
            course_id VARCHAR(255),
            course_name VARCHAR(255),
            credit VARCHAR(255),
            info VARCHAR(1000),
            antireq VARCHAR(500),
            offering VARCHAR(255),
            online BOOLEAN
        )"""
        self.execute(command)

    def create_prereqs(self):
        """
        Creates prereqs table.
        """
        command = "CREATE TABLE IF NOT EXISTS " + self.prereqs_table + """ (
            id SERIAL PRIMARY KEY,
            course_code VARCHAR(255),
            prereq VARCHAR(500),
            grades VARCHAR(250),
            not_open VARCHAR(250),
            only_from VARCHAR(250),
            min_level VARCHAR(10)
        )"""
        self.execute(command)

    def create_antireqs(self):
        """
        Creates antireqs table.
        """
        # TODO - implement & update SQL Config
        return ""

    def insert_prereqs(self, code, prereqs):
        """
        Inserts prereq data in prereqs table.

        :param code: string
        :param prereqs: Prereqs
        :return: boolean
        """
        not_exist = "SELECT 1 FROM " + self.prereqs_table + "\n"
        not_exist += "WHERE course_code = '" + code + "'"
        command = "INSERT INTO " + self.prereqs_table + " (course_code, prereq, grades, not_open, only_from, min_level)"
        command += "\nSELECT '" + code + "', '" + prereqs.str("prereqs") + "', '" + prereqs.str("grades") + "', '" + \
                   prereqs.str("not_open") + "', '" + prereqs.str("only") + "', '" + prereqs.str("level") + "'\n"
        command += "WHERE NOT EXISTS (\n" + not_exist + "\n);"

        return self.execute(command)

    def insert_course(self, course):
        """
        Inserts course data in course table.

        :param code: string
        :param course: Course
        :return: boolean
        """
        not_exist = "SELECT 1 FROM " + self.course_table + "\n"
        not_exist += "WHERE course_code = '" + course.code + "'"
        command = "INSERT INTO " + self.course_table + " (course_code, course_id, course_name, credit, info, " + \
                  "antireq, offering, online) "
        command += "SELECT '" + course.code + "', '" + course.id + "', '" + course.name + "', '" + \
                   str(course.credit) + "', '" + course.info.replace("'", "''") + "', '" + course.antireqs + \
                   "', '" + ",".join(course.offering) + "', " + str(course.online) + "\n"
        command += "WHERE NOT EXISTS (\n" + not_exist + "\n);"

        return self.execute(command)

    def insert_courses(self, courses):
        """
        Inserts courses into course table.

        :param courses: list(Course)
        :return: None
        """
        success = 0
        fail = 0
        for course in courses:
            if self.insert_prereqs(course.code, course.prereqs) and \
               self.insert_course(course):
                success += 1
            else:
                fail += 1

        root.info("Successfully inserted: %d rows", success)
        root.info("Failed to insert: %d rows", fail)
