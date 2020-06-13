from ProgramParsing.Science.MajorParser import ScienceMajorParser
from ProgramParsing.ProgramParser.ParseProgram import main
import os

if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'ProgramSpecs')
    files = set(["/ProgramSpecs/" + f for f in os.listdir(path) if f.endswith(".html")])

    main(ScienceMajorParser, files)
