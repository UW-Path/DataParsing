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
import os



class DatabaseConnection(object):
    def __init__(self, user="postgres", password="1234", host="localhost", port="5432", database="postgres",
                 course_table="course_info", prereqs_table="prereqs", antireqs_table="antireqs",
                 requirements_table = "requirements", communications_table="communications",
                 breadth_table="breadth_table"):
        if os.getenv("UWPATH_ENVIRONMENT") is not None and os.getenv("UWPATH_ENVIRONMENT") == "docker":
            host = "db"
        self.connection = psycopg2.connect(user=user, password=password, host=host, port=port, database=database)
        self.cursor = self.connection.cursor()
        self.course_table = course_table
        self.prereqs_table = prereqs_table
        self.antireqs_table = antireqs_table
        self.requirements_table = requirements_table
        self.communications_table = communications_table
        self.breadth_table = breadth_table

        self.root = self.__Logger()


    def __Logger(self):

        self.logger = logging.getLogger()
        if not len(self.logger.handlers):
            self.logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        return self.logger

    def execute(self, command):
        try:
            # self.root.info(command)
            self.cursor.execute(command)
            return True
        except Exception as e:
            print(command)
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

