from Database.DatabaseReceiver import DatabaseReceiver
import webbrowser as wb
import pandas as pd

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
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', 1200)

    course_codes = get_course_codes()
    course_codes.remove("FINE")  # For now
    course_codes.remove("ECON")  # For now
    print(course_codes)

    dbc = DatabaseReceiver()
    for code in course_codes:
        wb.open("http://www.ucalendar.uwaterloo.ca/2021/COURSE/course-" + code + ".html", new=2)
        print(dbc.get_course_info("WHERE course_code LIKE '" + code + " %'"))
        print(dbc.get_prereqs("WHERE course_code LIKE '" + code + " %'"))
        print(dbc.get_antireqs("WHERE course_code LIKE '" + code + " %'"))
        input()
