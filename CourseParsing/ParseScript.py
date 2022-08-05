from Database.DatabaseSender import DatabaseSender
from Database.DatabaseReceiver import DatabaseReceiver
from CourseParsing.CourseParser import CourseParser
import urllib.request
import traceback
from ProgramParsing.ProgramParser.ENV_VARIABLES.PARSE_YEAR import CALENDAR_YEARS

def get_course_codes():
    dbc = DatabaseReceiver()
    course_code_query = dbc.select(what="course_codes", table="requirements")
    course_codes = []
    for cc in course_code_query:
        codes = cc[0].split(", ")
        for c in codes:
            c = c.split()
            if len(c):
                course_codes.add(c[0])
    dbc.close()
    return course_codes


if __name__ == "__main__":
    course_codes = ['PACS', 'MATBUS', 'HLTH', 'ME', 'ARBUS', 'MSCI', 'ACTSC', 'CHE', 'CHEM', 'STAT',
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
                    'THPERF', 'UNIV', 'VCULT']

    dbc = DatabaseSender()

    dbc.drop_table(dbc.antireqs_table)
    dbc.drop_table(dbc.prereqs_table)
    dbc.drop_table(dbc.communications_table)
    dbc.drop_table(dbc.breadth_table)
    dbc.drop_table(dbc.course_table)

    dbc.create_courses()
    dbc.create_prereqs()
    dbc.create_antireqs()
    for year in CALENDAR_YEARS:
        #parse 20XX-20YY s.t year_str = XXYY, Parse from the most current years because it has the most accurate prereqs, etc..
        year_str = year[2:4] + year[7: 9]
        for code in reversed(course_codes):
            parser = CourseParser()
            try:
                fp = urllib.request.urlopen(f"http://www.ucalendar.uwaterloo.ca/{year_str}/COURSE/course-{code}.html")
                mybytes = fp.read()
                html = mybytes.decode("ISO-8859-1")
                fp.close()

                parser.load_html(html)
            except Exception as e:
                print(code)
                traceback.print_exc()
                continue

            dbc.insert_courses(parser.courses)

            dbc.commit()

    dbc.close()
