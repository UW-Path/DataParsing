from ProgramParsing.AHS.MajorParser import AHSMajorParser
from ProgramParsing.AHS.MajorParser2021_2022 import AHSMajorParser2021_2022
from ProgramParsing.ProgramParser.ParseProgram import main, filterFiles
import os

if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'Specs')
    files = set(["/Specs/" + f for f in os.listdir(path) if f.endswith(".html")])

    filesToIgnore = []
    files = filterFiles(files, filesToIgnore)

    # for testing purposes
    # files = set(["/Specs/2021-2022-HEA-Honours-Health-Studies.html"])

    parsers = {
        'MajorParser': AHSMajorParser,
        'MajorParser2021_2022': AHSMajorParser2021_2022
    }

    main(parsers, files, "Applied Health Science")
