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
    course_codes = {'PACS', 'MATBUS', 'HLTH', 'ME', 'ARBUS', 'MSCI', 'ACTSC', 'CHE', 'CHEM', 'STAT',
                    'CS', 'CO', 'GENE', 'EMLS', 'FINE', 'AMATH', 'BIOL', 'PMATH', 'LS', 'AFM', 'ENGL', 'KIN',
                    'SE', 'SPCOM', 'PSYCH', 'SYDE', 'MATH', 'INTEG', 'MTE', 'ECON', 'ECE', 'PHYS',
                    'MUSIC', 'HRM', 'ASL', 'ANTH', 'AHS', 'APPLS', 'ARABIC', 'AE', 'ARCH', 'ARTS', 'AVIA',
                    'BME', 'BASE', 'BET', 'CDNST', 'CHINA', 'CMW', 'CIVE', 'CLAS', 'COGSCI', 'COMM', 'COOP',
                    'CROAT', 'CI', 'DAC', 'DUTCH', 'EARTH', 'EASIA', 'ENBUS', 'ERS', 'ENVE', 'ENVS', 'FR',
                    'GSJ', 'GEOG', 'GEOE', 'GER', 'GERON', 'GBDA', 'GRK', 'HIST', 'HRTS', 'HUMSC', 'INDG',
                    'INDEV', 'INTST', 'ITAL', 'ITALST', 'JAPAN', 'JS', 'KIN', 'KOREA', 'LAT', 'LS',
                    'MGMT', 'MNS', 'MTHEL', 'ME', 'MTE', 'MEDVL', 'MENN', 'MOHAWK', 'NE', 'OPTOM', 'PHARM',
                    'PHIL', 'PLAN', 'PSCI', 'PORT', 'PD', 'PDARCH', 'PDPHRM', 'REC', 'RS', 'RUSS', 'REES',
                    'SCI', 'SCBUS', 'SMF', 'SDS', 'SVENT', 'SOCWK', 'SWREN', 'STV', 'SOC', 'SPAN', 'SI',
                    'THPERF', 'UNIV', 'VCULT'}

    dbc = DatabaseSender()

    dbc.create_courses()
    dbc.create_prereqs()
    dbc.create_antireqs()

    for code in course_codes:
        parser = CourseParser()

        try:
            fp = urllib.request.urlopen("http://www.ucalendar.uwaterloo.ca/2021/COURSE/course-" + code + ".html")
            mybytes = fp.read()
            html = mybytes.decode("ISO-8859-1")
            fp.close()

            parser.load_html(html)
        except Exception as e:
            print(code)
            print(e)
            continue

        dbc.insert_courses(parser.courses)

        dbc.commit()

    dbc.close()
