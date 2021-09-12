from ProgramParsing.Engineering.MajorParser import EngineeringMajorParser
from ProgramParsing.Engineering.MajorParser2021_2022 import EngineeringMajorParser2021_2022
from ProgramParsing.ProgramParser.ParseProgram import main, filterFiles
import os

if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'Specs')
    files = set(["/Specs/" + f for f in os.listdir(path) if f.endswith(".html")])

    filesToIgnore = []
    files = filterFiles(files, filesToIgnore)

    # files = set(["/Specs//ENG-Environmental-Engineering.html"])

    #Multople TE does not display
    # files = set(["/Specs/2021-2022-ENG-Electrical-Engineering.html"])

    parsers = {
        'MajorParser': EngineeringMajorParser,
        'MajorParser2021_2022': EngineeringMajorParser2021_2022
    }

    main(parsers, files, "Engineering")
