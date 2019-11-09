"""
DatabaseSender.py sends information about UW courses to an SQL database for later use.

Contributors:
Calder Lund
Hao Wei Huang
"""

from Database.DatabaseConnection import DatabaseConnection


class DatabaseSender(DatabaseConnection):
    def __init__(self):
        DatabaseConnection.__init__(self)

    def create_requirements(self):
        """
        create requirements table for each major
        """
        command = "CREATE TABLE IF NOT EXISTS "  + self.requirements_table + """ (
            id SERIAL PRIMARY KEY,
            program_name VARCHAR(255),
            plan_type VARCHAR(255),
            course_codes VARCHAR(255),
            number_of_courses int,
            additional_requirements VARCHAR(255) 
        );
        """
        self.execute(command)

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
            info VARCHAR(2000),
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

    def create_coreqs(self):
        """
        Creates coreqs table.
        """
        command = "CREATE TABLE IF NOT EXISTS " + self.coreqs_table + """ (
            id SERIAL PRIMARY KEY,
            course_code VARCHAR(255),
            coreq VARCHAR(500)
        )"""
        self.execute(command)

    def create_antireqs(self):
        """
        Creates antireqs table.
        """
        command = "CREATE TABLE IF NOT EXISTS " + self.antireqs_table + """ (
            id SERIAL PRIMARY KEY,
            course_code VARCHAR(255),
            antireq VARCHAR(500),
            extra_info VARCHAR(500)
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
        command = "INSERT INTO " + self.prereqs_table + " (course_code, prereq, grades, not_open, only_from, min_level)"
        command += "\nSELECT '" + code + "', '" + prereqs.str("prereqs") + "', '" + prereqs.str("grades") + "', '" + \
                   prereqs.str("not_open") + "', '" + prereqs.str("only") + "', '" + prereqs.str("level") + "'\n"
        command += "WHERE NOT EXISTS (\n" + not_exist + "\n);"

        return self.execute(command)

    def insert_coreqs(self, code, coreqs):
        """
        Inserts coreq data in coreqs table.

        :param code: string
        :param coreqs: Antireq
        :return: boolean
        """
        not_exist = "SELECT 1 FROM " + self.coreqs_table + "\n"
        not_exist += "WHERE course_code = '" + code + "'"
        command = "INSERT INTO " + self.coreqs_table + " (course_code, coreq)"
        command += "\nSELECT '" + code + "', '" + coreqs.str("coreqs") + "'\n"
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
                  "offering, online) "
        command += "SELECT '" + course.code + "', '" + course.id + "', '" + course.name + "', '" + \
                   str(course.credit) + "', '" + course.info.replace("'", "''") + "', '" + ",".join(course.offering) + \
                   "', " + str(course.online) + "\n"
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
                    self.insert_coreqs(course.code, course.prereqs) and \
                    self.insert_antireqs(course.code, course.antireqs) and \
                    self.insert_course(course):
                success += 1
            else:
                fail += 1

        self.root.info("Successfully inserted: %d rows", success)
        self.root.info("Failed to insert: %d rows", fail)

    def insert_requirement(self, requirement):
        """

        :param requirement: MajorReq
        :return: None
        """
        not_exist = "SELECT 1 FROM " + self.requirements_table + "\n"
        not_exist += "WHERE course_codes = '" + requirement.courseCodes + "' AND program_name = '" + requirement.programName + "'"

        command = "INSERT INTO " + self.requirements_table + " (program_name, plan_type, course_codes, number_of_courses, additional_requirements) "
        command += "SELECT '" + requirement.programName + "', '" + requirement.planType + "', '" + requirement.courseCodes + "', " + str(requirement.numberOfCourses)
        command += ", '" + requirement.additionalRequirement + "'"
        command += " WHERE NOT EXISTS (\n" + not_exist + "\n);"

        return self.execute(command)

    def insert_requirements(self, requirements):
        """
        Inserts requirements into requirements table.

        :param requirements: list(MajorReq)
        :return: None
        """
        success = 0
        fail = 0

        for req in requirements:
            if self.insert_requirement(req):
                success += 1
            else:
                fail += 1

        self.root.info("Successfully inserted: %d rows", success)
        self.root.info("Failed to insert: %d rows", fail)
