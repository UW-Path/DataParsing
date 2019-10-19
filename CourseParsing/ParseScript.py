from Database import DatabaseConnection
from CourseParsing.CourseParser import CourseParser

if __name__ == "__main__":
    file = "CoursesMATH1920.html"

    parser = CourseParser()
    parser.load_file(file)

    dbc = DatabaseConnection()

    dbc.create_courses()
    dbc.create_prereqs()
    dbc.create_antireqs()

    dbc.insert_courses(parser.courses)

    dbc.commit()
    dbc.close()