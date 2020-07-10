from ProgramParsing.Engineering.MajorParser import EngineeringMajorParser
from ProgramParsing.ProgramParser.ParseProgram import main
import os

if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'Specs')
    files = set(["/Specs/" + f for f in os.listdir(path) if f.endswith(".html")])

    filesToIgnore = []
    filesToIgnore = set(["/Specs/" + f for f in filesToIgnore])
    files = files - filesToIgnore

    # files = set(["/Specs//ENG-Environmental-Engineering.html"])

    #Multople TE does not display
    # files = set(["/Specs/ENG-Mechatronics-Engineering.html"])

    main(EngineeringMajorParser, files, "Engineering")
