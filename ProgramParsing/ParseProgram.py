from Database.DatabaseSender import DatabaseSender
from ProgramParsing.MajorParser import MajorParser
import os

if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'ProgramSpecs')
    files = ["/ProgramSpecs/" + f for f in os.listdir(path) if f.endswith(".html")]
    files.append("TableII.html")

    #Need to Investigate
    filesToIgnore = ["ENG-Software-Engineering.html", "MATH-Math-or-Fin-Analysis-Risk-Mgt-Degree-Reqmnt.html",
                     "MATH-Mathematical-Optimization1.html",]
    filesToIgnore = ["/ProgramSpecs/" + f for f in filesToIgnore]

    #files = ["/ProgramSpecs/MATH-Joint-Pure-Mathematics1.html"] #use this for single files

    #TODO parse which specialization is under which major

    dbc = DatabaseSender()

    dbc.execute("DROP TABLE " + dbc.requirements_table + ";")
    dbc.create_requirements()

    for file in files:
        if (file in filesToIgnore): continue
        print("CURRENT FILE PARSING : " + file)
        parser = MajorParser()
        parser.load_file(file)

        print(parser)

        # Parser requirement is a list of MajorReq Object
        dbc.insert_requirements(parser.requirement)
        dbc.commit()

    dbc.close()