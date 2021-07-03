from ProgramParsing.Arts.MajorParser import ArtsMajorParser
from ProgramParsing.ProgramParser.ParseProgram import main, filterFiles
import os

if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'Specs')
    files = set(["/Specs/" + f for f in os.listdir(path) if f.endswith(".html")])

    filesToIgnore = ["ARTS-BA-Degree-Requirements.html"]
    files = filterFiles(files, filesToIgnore)

    # files =["Specs/ARTS-BAFM-Degree-Requirements.html"]

    parsers = {
        'MajorParser': ArtsMajorParser,
    }

    main(parsers, files, "Arts")
