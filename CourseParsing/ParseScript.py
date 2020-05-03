from Database.DatabaseSender import DatabaseSender
from Database.DatabaseReceiver import DatabaseReceiver
from CourseParsing.CourseParser import CourseParser
import urllib.request

def get_course_codes():
    dbc = DatabaseReceiver()
    course_code_query = dbc.select(what="course_codes", table="requirements")
    course_codes = set([])
    for cc in course_code_query:
        codes = cc[0].split(", ")
        for c in codes:
            c = c.split()
            if len(c):
                course_codes.add(c[0])
    dbc.close()
    return course_codes


if __name__ == "__main__":
    course_codes = get_course_codes()

    dbc = DatabaseSender()

    dbc.execute("DROP TABLE " + dbc.course_table + ";")
    dbc.execute("DROP TABLE " + dbc.prereqs_table + ";")
    dbc.execute("DROP TABLE " + dbc.coreqs_table + ";")
    dbc.execute("DROP TABLE " + dbc.antireqs_table + ";")

    dbc.create_courses()
    dbc.create_prereqs()
    dbc.create_coreqs()
    dbc.create_antireqs()

    for code in course_codes:
        parser = CourseParser()

        try:
            fp = urllib.request.urlopen("http://www.ucalendar.uwaterloo.ca/2021/COURSE/course-" + code + ".html")
        except Exception as e:
            print(code)
            continue
        mybytes = fp.read()
        html = mybytes.decode("ISO-8859-1")
        fp.close()

        parser.load_html(html)

        dbc.insert_courses(parser.courses)

        dbc.commit()

    dbc.close()
