"""
DatabaseConnection.py provides general PostgreSQL capabilities for UWPath in a class
called DatabaseConnection.

Contributors:
Calder Lund
Hao Wei Huang
"""

import psycopg2
import logging
import sys


class DatabaseConnection(object):
    def __init__(self, user="postgres", password="1234", host="localhost", port="8888", database="postgres",
                 course_table="course_info", prereqs_table="prereqs", coreqs_table="coreqs", antireqs_table="antireqs",
                 requirements_table = "requirements"):
        self.connection = psycopg2.connect(user=user, password=password, host=host, port=port, database=database)
        self.cursor = self.connection.cursor()
        self.course_table = course_table
        self.prereqs_table = prereqs_table
        self.coreqs_table = coreqs_table
        self.antireqs_table = antireqs_table
        self.requirements_table = requirements_table

        self.root = logging.getLogger()
        self.root.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.root.addHandler(handler)

    def execute(self, command):
        try:
            self.root.info(command)
            self.cursor.execute(command)
            return True
        except Exception as e:
            self.root.error(e)
            return False

    def commit(self):
        if self.connection:
            self.connection.commit()

    def close(self):
        self.connection.close()

    def select(self, what, table, condition=""):
        """
        SELECT <what> FROM <table> <condition>;

        :param what: string
        :param table: string
        :param condition: string
        :return: list
        """
        command = "SELECT " + what + " FROM " + table + " " + condition + ";"
        self.execute(command)
        return self.cursor.fetchall()
