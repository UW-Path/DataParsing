from Database.DatabaseSender import DatabaseSender

#TODO Make this dynamic
CALENDAR_YEAR = "2021-2022" #This needs to be updated manually every school year

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
        dbc.execute("DELETE FROM {req} WHERE YEAR='{year}'".format(req=dbc.requirements_table, year=CALENDAR_YEAR))

        # TODO: FOR PERSONAL RUN UNCOMMENT THESE LINES
        # dbc.execute("DROP TABLE IF EXISTS " + dbc.requirements_table + ";")
        # dbc.create_requirements()

    for file in files:
        print("CURRENT FILE PARSING : " + file)
        parser = majorParser()
        parser.load_file(file)

        # print(parser)

        link = get_link(file)
        # Parser requirement is a list of MajorReq Object
        dbc.insert_requirements(parser.requirement, faculty, link, CALENDAR_YEAR)
        dbc.commit()

    dbc.close()
