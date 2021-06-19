"""
CourseParser.py is a library built to receive information on Major Requirements

Contributors:
Hao Wei Huang
"""

import urllib3
from bs4 import BeautifulSoup
from ProgramParsing.Math.MajorReq import MajorReq
from StringToNumber import StringToNumber
import re
import pkg_resources


class MajorParser:
    def __init__(self):
        self.http = urllib3.PoolManager()
        self.data = None
        self.requirement = []
        self.additionalRequirement = ""

    def load_url(self, url):
        response = self.http.request('GET', url)
        self.data = BeautifulSoup(response.data, 'html.parser')

    def _has_numbers(self, input_string):
        """
                Check if input_string has numbers (0-9)
                :return: bool
        """
        return bool(re.search(r'\d', input_string))

    def _get_program(self):
        pass

    def _stringIsNumber(self, s):
        s = str(s).split(" ")[0].lower()
        if "one" in s or "two" in s or "three" in s or "four" in s or "five" in s \
                or "six" in s or "seven" in s or "eight" in s or "nine" in s or "ten" in s:
            return True
        else:
            return False

    def _getLevelCourses(self, string):
        return re.findall(r"[1-9][0-9][0-9]-", string)

    def _require_all(self, list, major, relatedMajor, additionalRequirement=None):
        pass

    def getAdditionalRequirement(self):
        additionalRequirment = []
        paragraphs = self.data.find_all(["p"]) # cant use span because will get everything else
        for p in paragraphs:
            # a bit hardcoded
            if ("all the requirements" in str(p) or "course requirements" in str(p) or "all requirements" in str(p)) and "plan" in str(p):
                reqs = p.find_all("a")
                print(reqs)
                for req in reqs:
                    # span added for special case for  PMATH additional req #does not work
                    if(not self._has_numbers(req.contents[0])):
                        additionalRequirment.append(req.contents[0])
        return ", ".join(additionalRequirment)

    def _get_relatedMajor(self, program):
        relatedMajor = self.data.find_all("span", id="ctl00_contentMain_lblTopTitle")
        if relatedMajor:
            relatedMajor = relatedMajor[0].contents[0].string
        else:
            return ""

        if "Academic Plans and Requirements" in relatedMajor:
            #check if program is minor
            if "minor" in program.lower():
                program = program.replace(" Minor", "")
            return program
        else:
            return relatedMajor

    def _course_list(self, info, i, oneOf = False):
        pass

    def _additional_list(self, info, i, multiLine):
        pass

    def is_additional(self, string):
        pass

    def load_file(self, file, year):
        """
                Parse html file to gather a list of required courses for the major

                :return:
        """
        return pkg_resources.resource_string(__name__, str(year)+"_"+file)

    def __str__(self):
        output = ""
        for req in self.requirement:
            output += str(req) + "\n"
        return output

