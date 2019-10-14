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

connectionString = psycopg2.connect(user="postgres",
                                    password="1234",
                                    host="localhost",
                                    port="8888",
                                    database="UWPath")


def insert_courses(courses):
    row = 0
    failed = 0
    for course in courses:
        if (insert_row_course_info(course)):
            row += 1
        else: failed +=1

    connection = connectionString
    connection.close()

    print("Successfuly inserted: %d rows", row)
    print("Failed to insert: %d rows", failed)


def insert_row_course_info(course):
    isError = False;
    try:
        connection = connectionString
        cursor = connection.cursor()

        # Print PostgreSQL version
        command = "INSERT INTO Course_Info (course_code, course_id, course_name, credit, info, prereq, antireq, offering, online) VALUES('" + course.code + "', "
        command += "'" + course.id + "', " + "'" + course.name + "', " + "'" + str(course.credit) + "', " + "'" +course.info.replace("'", "''")
        command += "', " + "'" + str(course.prereqs) + "', " + "'" + str(course.antireqs) +"', " + "'" + ",".join(course.offering) + "', " + str(course.online) + ")"

        cursor.execute(command)

    except (Exception, psycopg2.Error) as error :
        print("Error while connecting to PostgreSQL", error)
        isError = True
    finally:
        #closing database connection.
            if(connection):
                connection.commit()
                cursor.close()
            return not isError