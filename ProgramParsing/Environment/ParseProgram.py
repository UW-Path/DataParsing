from ProgramParsing.Environment.MajorParser import EnvironmentMajorParser
from ProgramParsing.ProgramParser.ParseProgram import main, filterFiles
import os

if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'Specs')
    files = set(["/Specs/" + f for f in os.listdir(path) if f.endswith(".html")])

    filesToIgnore = ["ENV-Env-Res-Sus-Env-Res-Stud-Hons-Reg-Co-op.html", "ENV-Honours-Environment-Business-Co-op-and-Reg.html",
                     "ENV-Honours-Geography-and-Aviation-Regular.html"]

    files = filterFiles(files, filesToIgnore)

    # files = set(["/Specs/ENV-Honours-International-Development.html"])
    #needs to be done

    parsers = {
        'MajorParser': EnvironmentMajorParser,
    }

    main(parsers, files, "Environment")
