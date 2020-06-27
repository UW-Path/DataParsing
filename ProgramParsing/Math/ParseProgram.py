from ProgramParsing.Math.MajorParser import MathMajorParser
from ProgramParsing.ProgramParser.ParseProgram import main
import os

if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'Specs')
    files = set(["/Specs/" + f for f in os.listdir(path) if f.endswith(".html")])
    files.add("TableII.html")

    filesToIgnore = ["ENG-Software-Engineering.html", "MATH-Math-or-Fin-Analysis-Risk-Mgt-Degree-Reqmnt.html",
                     "MATH-Mathematical-Optimization1.html", "MATH-Math-or-Chartered-Professional-Accountancy-co.html"]
    filesToIgnore = set(["/Specs/" + f for f in filesToIgnore])
    files = files - filesToIgnore

    # files = set(["/Specs/MATH-AM-Degree-Requirements-Applied-Mathematics.html"])

    main(MathMajorParser, files, DropTable=True)
