from ProgramParsing.Math.MajorParser import MathMajorParser
from ProgramParsing.Math.MajorParser2021_2022 import MathMajorParser2021_2022
from ProgramParsing.ProgramParser.ParseProgram import main, filterFiles
import os

# For now, we should have a default MathMajorParser and a parser for every year
# Purpose is to keep changes in scope (so we won't end up creating more bugs for one year)

if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'Specs')
    files = set(["/Specs/" + f for f in os.listdir(path) if f.endswith(".html")])
    files.add("TableII.html")

    filesToIgnore = ["ENG-Software-Engineering.html",
                     "MATH-Mathematical-Optimization1.html", "MATH-Math-or-Chartered-Professional-Accountancy-co.html"]

    # adds year in front of files in filesToIgnore
    files = filterFiles(files, filesToIgnore)

    # files = set(["/Specs/2021-2022-MATH-Joint-Pure-Mathematics1.html"])

    # put parsers into a dictionary
    parsers = {
            'MajorParser': MathMajorParser,
            'MajorParser2021_2022': MathMajorParser2021_2022
            }

    main(parsers, files, DropTable=True)
