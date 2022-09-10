"""
DatabaseConnection.py provides general PostgreSQL capabilities for UWPath in a class
called DatabaseConnection.

Contributors:
Calder Lund
Hao Wei Huang
"""

import logging
import sys
import os
import oracledb


class DatabaseConnection(object):
    connection = None
    def __init__(self, course_table="course_info", prereqs_table="prereqs", antireqs_table="antireqs",
                 requirements_table="requirements", communications_table="communications",
                 breadth_table="breadth_table"):
        password = os.getenv("DB_PASS")
        user = os.getenv("DB_USER")
        dsn = os.getenv("ORACLE_DSN")
        env = os.getenv("UWPATH_ENVIRONMENT")
        
        try:
            if DatabaseConnection.connection is None or DatabaseConnection.ping():
                if env is not None:
                    wallet_location = os.getenv("TNS_ADMIN");
                    print("Connecting to cloud db")
                    DatabaseConnection.connection = oracledb.connect(user = user, password = password, dsn = dsn, config_dir = wallet_location, wallet_location=wallet_location, wallet_password = password)
                else:
                    DatabaseConnection.connection = oracledb.connect(user = user, password = password, dsn = dsn)
                print("Successfully connected to db")
        except Exception as err:
            print("Whoops!")
            print(err);
            sys.exit(1);
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
            print(command)
            self.cursor.execute(command)
            return True
        except Exception as e:
            print(command)
            self.root.error(e)
            sys.exit(1)

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
        command = "SELECT " + what + " FROM " + table + " " + condition
        self.execute(command)
        return self.cursor.fetchall()
    
    def drop_table(self, table) :
        query = """
        declare
            c int;
        begin
            select count(*) into c from user_tables where table_name = upper('{table}');
            if c = 1 then
                execute immediate 'drop table {table}';
            end if;
        end;
        """
        self.execute(query.format(table = table))
