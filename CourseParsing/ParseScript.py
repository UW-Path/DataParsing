from Database import DatabaseConnection
from CourseParsing.CourseParser import CourseParser

if __name__ == "__main__":
    files = ["CoursesACTSC1920.html", "CoursesAMATH1920.html", "CoursesCO1920.html", "CoursesCS1920.html",
             "CoursesMATH1920.html", "CoursesPMATH1920.html", "CoursesSTAT1920.html"]

    dbc = DatabaseConnection()

    dbc.create_courses()
    dbc.create_prereqs()
    dbc.create_coreqs()
    dbc.create_antireqs()

    for file in files:
        parser = CourseParser()
        parser.load_file(file)

        dbc.insert_courses(parser.courses)

        dbc.commit()

    dbc.close()
