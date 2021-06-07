"""
DatabaseSender.py sends information about UW courses to an SQL database for later use.

Contributors:
Calder Lund
Hao Wei Huang
"""

from Database.DatabaseConnection import DatabaseConnection
import re


class DatabaseSender(DatabaseConnection):
    def __init__(self):
        DatabaseConnection.__init__(self)

    def create_requirements(self):
        """
        create requirements table for each major
        """
        command = "CREATE TABLE " + self.requirements_table + """ (
            id SERIAL PRIMARY KEY,
            program_name VARCHAR(255),
            plan_type VARCHAR(255),
            course_codes VARCHAR(5000),
            number_of_courses int,
            credits_required DECIMAL(4,2),
            additional_requirements VARCHAR(255), 
            major_name VARCHAR(255),
            faculty VARCHAR(50),
            link VARCHAR(255),
            year VARCHAR(20)
        )
        """
        self.execute(command)

    def create_courses(self):
        """
        Creates courses table.
        """
        # TODO - remove antireq field
        command = "CREATE TABLE IF NOT EXISTS " + self.course_table + """ (
            course_code VARCHAR(255) PRIMARY KEY,
            course_abbr VARCHAR(10),
            course_number INT,
            course_id VARCHAR(255),
            course_name VARCHAR(255),
            credit VARCHAR(255),
            info VARCHAR(2000),
            offering VARCHAR(255),
            online BOOLEAN,
            prereqs VARCHAR(500),
            coreqs VARCHAR(500),
            antireqs VARCHAR(500)
        )"""
        self.execute(command)

    def create_prereqs(self):
        """
        Creates prereqs table.
        """
        command = "CREATE TABLE IF NOT EXISTS " + self.prereqs_table + """ (
            course_code VARCHAR(255) PRIMARY KEY,
            logic VARCHAR(500),
            courses VARCHAR(500),
            grades VARCHAR(250),
            not_open VARCHAR(250),
            only_from VARCHAR(250),
            min_level VARCHAR(10),
            FOREIGN KEY ( course_code ) REFERENCES """ + self.course_table + """ ( course_code )
        )"""
        self.execute(command)

    def create_antireqs(self):
        """
        Creates antireqs table.
        """
        command = "CREATE TABLE IF NOT EXISTS " + self.antireqs_table + """ (
            course_code VARCHAR(255) PRIMARY KEY,
            antireq VARCHAR(500),
            extra_info VARCHAR(500),
            FOREIGN KEY ( course_code ) REFERENCES """ + self.course_table + """ ( course_code )
        )"""
        self.execute(command)

    def create_communications(self):
        """
        Creates communications table.
        """
        command = "CREATE TABLE IF NOT EXISTS " + self.communications_table + """ (
            id SERIAL PRIMARY KEY,
            course_code VARCHAR(255),
            list_number INT,
            FOREIGN KEY ( course_code ) REFERENCES """ + self.course_table + """ ( course_code )
        )"""
        self.execute(command)

    def create_breadth(self):
        """
        Creates breadth table.
        """
        command = "CREATE TABLE IF NOT EXISTS " + self.breadth_table + """ (
            subject VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            humanities BOOLEAN,
            social_science BOOLEAN,
            pure_science BOOLEAN,
            applied_science BOOLEAN
        )"""
        self.execute(command)

    def insert_prereqs(self, code, prereqs):
        """
        Inserts prereq data in prereqs table.

        :param code: string
        :param prereqs: Prereqs
        :return: boolean
        """
        not_exist = "SELECT 1 FROM " + self.prereqs_table + "\n"
        not_exist += "WHERE course_code = '" + code + "'"
        command = "INSERT INTO " + self.prereqs_table + \
                  " (course_code, logic, courses, grades, not_open, only_from, min_level)"
        command += "\nSELECT '" + code + "', '" + prereqs.str("logic") + "', '" + prereqs.str("courses") + "', '" + \
                   prereqs.str("grades") + "', '" + prereqs.str("not_open") + "', '" + prereqs.str("only") + \
                   "', '" + prereqs.str("level") + "'\n"
        command += "WHERE NOT EXISTS (\n" + not_exist + "\n);"

        return self.execute(command)

    def insert_antireqs(self, code, antireqs):
        """
        Inserts antireq data in antireqs table.

        :param code: string
        :param antireqs: Antireq
        :return: boolean
        """
        not_exist = "SELECT 1 FROM " + self.antireqs_table + "\n"
        not_exist += "WHERE course_code = '" + code + "'"
        command = "INSERT INTO " + self.antireqs_table + " (course_code, antireq, extra_info)"
        command += "\nSELECT '" + code + "', '" + antireqs.str("antireqs") + "', '" + antireqs.str("extra") + "'\n"
        command += "WHERE NOT EXISTS (\n" + not_exist + "\n);"

        return self.execute(command)

    def insert_communication(self, code, list_num):
        """
        Inserts communication data in communication table.

        :param code: string
        :param list_num: int
        :return: boolean
        """
        not_exist = "SELECT 1 FROM " + self.communications_table + "\n"
        not_exist += "WHERE course_code = '" + code + "'"
        command = "INSERT INTO " + self.communications_table + " (course_code, list_number)"
        command += "\nSELECT '" + code + "', " + str(list_num) + "\n"
        command += "WHERE NOT EXISTS (\n" + not_exist + "\n);"

        return self.execute(command)

    def insert_breadth(self, breadth_data):
        """
        Inserts breadth data in breadth table.

        :param breadth_data: list
        :return: boolean
        """
        not_exist = "SELECT 1 FROM " + self.breadth_table + "\n"
        not_exist += "WHERE subject = '" + breadth_data["subject"] + "'"
        command = "INSERT INTO " + self.breadth_table
        command += " (subject, name, humanities, social_science, pure_science, applied_science)"
        command += "\nSELECT '" + breadth_data["subject"] + "', '" + breadth_data["name"] + "', "
        command += str(breadth_data["humanities"]) + ", " + str(breadth_data["social_science"]) + ", "
        command += str(breadth_data["pure_science"]) + ", " + str(breadth_data["applied_science"]) + "\n"
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
        not_exist += "WHERE course_code = '" + course.course_code + "'"
        command = "INSERT INTO " + self.course_table + " (course_code, course_abbr, course_number, course_id, " \
                                                       "course_name, credit, info, offering, online, prereqs," \
                                                       " coreqs, antireqs) "
        command += "SELECT '" + course.course_code + "', '" + course.course_abbr + "', " + re.sub("[^0-9]", "", course.course_number) + \
                   ", '" + course.id + "', '" + course.name + "', '" + str(course.credit) + "', '" + \
                   course.info.replace("'", '"') + "', '" + ",".join(course.offering) + "', " + str(course.online) + \
                   ", '" + course.prereq_text.replace("'", '"') + "', '" + course.coreq_text.replace("'", '"') + \
                   "', '" + course.antireq_text.replace("'", '"') + "'\n"
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
            if self.insert_course(course) and self.insert_prereqs(course.course_code, course.prereqs) and \
                    self.insert_antireqs(course.course_code, course.antireqs):
                success += 1
            else:
                fail += 1

        self.root.info("Successfully inserted: %d rows", success)
        self.root.info("Failed to insert: %d rows", fail)

    def insert_requirement(self, requirement, faculty, link, year):
        """

        :param requirement: MajorReq
        :return: None
        """
        not_exist = "SELECT 1 FROM " + self.requirements_table + "\n"
        not_exist += "WHERE course_codes = '" + requirement.courseCodes + "' AND program_name = '" + requirement.programName + "' AND major_name = '" + requirement.majorName + \
        "' AND credits_required= " + str(requirement.credits) + " AND additional_requirements= '" + requirement.additionalRequirement + "' AND year= '" + year + "'"

        command = "INSERT INTO " + self.requirements_table + " (program_name, plan_type, course_codes, number_of_courses, credits_required, additional_requirements, major_name, faculty, link, year) "
        command += "SELECT '" + requirement.programName + "', '" + requirement.planType + "', '" + requirement.courseCodes + "', " + str(requirement.numberOfCourses) + ", " + str(requirement.credits)
        command += ", '" + requirement.additionalRequirement + "', '" + requirement.majorName + "', '" + faculty + "', " + "'" + link + "', '" + year + "'"
        command += " WHERE NOT EXISTS (\n" + not_exist + "\n);"

        return self.execute(command)

    def insert_requirements(self, requirements, faculty, link, year):
        """
        Inserts requirements into requirements table.

        :param requirements: list(MajorReq)
        :return: None
        """
        success = 0
        fail = 0

        for req in requirements:
            if self.insert_requirement(req, faculty, link, year):
                success += 1
            else:
                fail += 1

        self.root.info("Successfully inserted: %d rows", success)
        self.root.info("Failed to insert: %d rows", fail)
