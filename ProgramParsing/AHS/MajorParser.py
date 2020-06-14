"""
MajorParser.py is a library built to receive information on Major Requirements

Contributors:
Hao Wei Huang
Calder Lund
"""

from ProgramParsing.AHS.MajorReq import AHSMajorReq
from ProgramParsing.ProgramParser.MajorParser import MajorParser
import pkg_resources
from bs4 import BeautifulSoup
import re

class AHSMajorParser(MajorParser):
    def _get_program(self):
        program = self.data.find_all("span", id="ctl00_contentMain_lblPageTitle")

        if program:
            program = program[0].contents[0].string
            if ", " in program:
                program = program.split(", ")[1]

        return program

    def load_file(self, file):
        """
                Parse html file to gather a list of required courses for the major

                :return:
        """
        html = pkg_resources.resource_string(__name__, file)
        # html = open(file, encoding="utf8")
        self.data = BeautifulSoup(html, 'html.parser')

        program = self._get_program()

        # Find all additional requirement
        self.additionalRequirement = self.getAdditionalRequirement()

        information = self.data.find("span", {'class': 'MainContent'}).get_text().split("\n")

        print(program)

        i = 0
        while i < len(information):
            line = information[i]
            if "Course Sequence" in line or "Note" in line or "General" in line:
                break
            if "equired" in line or "unit" in line or len(re.findall(r"[A-Z]{2,10}", line)):
                # Create major reqs
                i += 1
