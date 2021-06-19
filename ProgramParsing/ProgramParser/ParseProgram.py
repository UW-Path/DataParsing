from Database.DatabaseSender import DatabaseSender

# Must be in this format
CALENDAR_YEARS = ["2018-2019", "2019-2020", "2020-2021"]

def get_link(file):
    #clean up
    file = file.replace("/Specs/", "").replace(".html", "")
    if "table" in file.lower():
        # special case for table 1/table 2 in math
        file = "MATH-Degree-Requirements-for-Math-students"
    return "https://ugradcalendar.uwaterloo.ca/page/" + file

def main(majorParser, files, faculty="Math", DropTable=False):
    dbc = DatabaseSender()
    if DropTable:
        dbc.execute("DROP TABLE IF EXISTS " + dbc.requirements_table + ";")
        dbc.create_requirements()

    for file in files:
        print("CURRENT FILE PARSING : " + file)
        parser = majorParser()
        parser.load_file(file)

        # print(parser)

        link = get_link(file)
        # Parser requirement is a list of MajorReq Object
        calendar_year = get_calendar_year(file) # must implement this after implementing UpdateDegreeRequirement properly
        dbc.insert_requirements(parser.requirement, faculty, link, calendar_year)
        dbc.commit()

    dbc.close()
