from ProgramParsing.Science.MajorParser import ScienceMajorParser
from ProgramParsing.Science.MajorParser2021_2022 import ScienceMajorParser2021_2022
from ProgramParsing.ProgramParser.ParseProgram import main, filterFiles
import os

if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'Specs')
    files = set(["/Specs/" + f for f in os.listdir(path) if f.endswith(".html")])
    filesToIgnore = []
    files = filterFiles(files, filesToIgnore)

    # Debugging purposes
    # files = set(["/Specs/SCI-Honours-Science5.html"])

    # put parsers into a dictionary
    parsers = {
            'MajorParser': ScienceMajorParser,
            'MajorParser2021_2022': ScienceMajorParser2021_2022
            }

    main(parsers, files, "Science")

