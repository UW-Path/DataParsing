from ProgramParsing.Science.MajorParser import ScienceMajorParser
from ProgramParsing.ProgramParser.ParseProgram import main
import os

if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'Specs')
    files = set(["/Specs/" + f for f in os.listdir(path) if f.endswith(".html")])

    # Debugging purposes
    #files = set(["/Specs/Sci-Astrophysics-Minor.html"])
    main(ScienceMajorParser, files, "Science")

