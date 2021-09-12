from Database.DatabaseSender import DatabaseSender
from ProgramParsing.ProgramParser.ENV_VARIABLES.PARSE_YEAR import PARSE_YEAR_BEG, PARSE_YEAR_END, CALENDAR_YEARS, DEFAULT_YEAR
import re



def filterFiles(files, filesToIgnore):
    # adds the academic year in front of strings in filesToIgnore
    filesToIgnoreYear = []
    for year in range(PARSE_YEAR_BEG, PARSE_YEAR_END + 1):
        for fti in filesToIgnore:
            year_range = str(year) + "-" + str(year + 1) + "-"
            filesToIgnoreYear.append(year_range + fti)
    filesToIgnore = set(["/Specs/" + f for f in filesToIgnoreYear])
    files = files - filesToIgnore

    return files


def get_link(file, calendar_year):
    #clean up
    file = file.replace("/Specs/", "").replace(".html", "")
    # removes the calendar_year from the file name
    if calendar_year in file:
        file = file.replace(calendar_year + "-", "")
    if "table" in file.lower():
        # special case for table 1/table 2 in math
        file = "MATH-Degree-Requirements-for-Math-students"

    #note: frontend takes care of the year param - just need root link here
    return "https://ugradcalendar.uwaterloo.ca/page/" + file


def getMajorParser(parsers, year):
    year = year.replace("-", "_") #syntax

    if "MajorParser" + year in parsers:
        return parsers["MajorParser" + year]
    else:
        #default parser
        return parsers["MajorParser"]


def get_calendar_year(file):
    # get year from file: regex matching 20xx-20xx
    res = re.findall(r"20[0-9]{2}-20[0-9]{2}", file)
    if res:
        return res[0]
    else:
        print("Warning: This file does not have a year")
        return DEFAULT_YEAR

# majorParsers is a dict with different class instances of a parser
def main(majorParsers, files, faculty="Math", DropTable=False):
    dbc = DatabaseSender()
    if DropTable:
        dbc.execute("DROP TABLE IF EXISTS " + dbc.requirements_table + ";")
        dbc.create_requirements()

    total = 0
    for file in files:
        calendar_year = get_calendar_year(file) # must implement this after implementing UpdateDegreeRequirement properly

        # Info: the following block of code is for debugging purposes. Feel free to change CALENDAR_YEARS
        if calendar_year not in CALENDAR_YEARS: continue

        print("CURRENT FILE PARSING : " + file)

        parser = getMajorParser(majorParsers, calendar_year)
        parser = parser()
        parser.load_file(file, calendar_year)
        link = get_link(file, calendar_year)

        total += len(parser.requirement)

        # Parser requirement is a list of MajorReq Object
        dbc.insert_requirements(parser.requirement, faculty, link, calendar_year)
        dbc.commit()


    dbc.close()