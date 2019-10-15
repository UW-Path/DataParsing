"""
Database.py receives information about UW courses and sends that information
to an SQL database for later use.

Date:
October 13th, 2019

Contributors:
Calder Lund
Hao Wei Huang
"""

import psycopg2


def insert_courses(courses, user="postgre", password="1234", host="localhost", port="8888", database="UWPath"):
    """
    Inserts information from Course objects into an SQL database given the following variables
    for the database connection string.

    :param courses: list(Course)
    :param user: string
    :param password: string
    :param host: string
    :param port: string
    :param database: string
    :return:
    """
    row = 0
    failed = 0

    try:
        connection = psycopg2.connect(user=user, password=password, host=host, port=port, database=database)
    except (Exception, psycopg2.Error) as error:
        raise error

    for course in courses:
        if insert_row_course_info(course, connection):
            row += 1
        else:
            failed += 1

    connection.close()

    print("Successfully inserted: %d rows", row)
    print("Failed to insert: %d rows", failed)


def insert_row_course_info(course, connection):
    """
    Inserts individual course into a row of the database given the connection to the database.

    :param course: Course
    :param connection: connection
    :return: boolean
    """
    try:
        cursor = connection.cursor()

        # Print PostgreSQL version
        command = "INSERT INTO Course_Info (course_code, course_id, course_name, credit, info, prereq, " + \
                  "antireq, offering, online) "
        command += "VALUES('" + course.code + "', '" + course.id + "', '" + course.name + "', '" + \
                   str(course.credit) + "', '" + course.info.replace("'", "''") + "', '" + course.prereqs + \
                   "', '" + course.antireqs + "', '" + ",".join(course.offering) + "', " + str(course.online) + ")"

        cursor.execute(command)

        # committing database connection.
        if connection:
            connection.commit()

        return True

    except (Exception, psycopg2.Error) as error:
        print(error)
        return False
