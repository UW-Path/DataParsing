from ProgramParsing.Environment.MajorParser import EnvironmentMajorParser
from ProgramParsing.Environment.MajorParser2021_2022 import EnvironmentMajorParser2021_2022
from ProgramParsing.ProgramParser.ParseProgram import main, filterFiles
import os

if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'Specs')
    files = set(["/Specs/" + f for f in os.listdir(path) if f.endswith(".html")])

    filesToIgnore = ["ENV-Env-Res-Sus-Env-Res-Stud-Hons-Reg-Co-op.html", "ENV-Honours-Environment-Business-Co-op-and-Reg.html",
                     "ENV-Honours-Geography-and-Aviation-Regular.html"]

    files = filterFiles(files, filesToIgnore)

    #files = set(["/Specs/" + "2021-2022-ENV-Honours-Environment-Resources-Sustainability.html"])
    #needs to be done

    parsers = {
        'MajorParser': EnvironmentMajorParser,
        'MajorParser2021_2022': EnvironmentMajorParser2021_2022
    }

    main(parsers, files, "Environment")
