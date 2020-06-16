"""
Major is an object class that stores information for major requirements

Contributors:
Calder Lund
"""

from ProgramParsing.ProgramParser.MajorReq import MajorReq


class AHSMajorReq(MajorReq):
    def __init__(self, list, program, relatedMajor, additionalRequirement, credits):
        self.list = list
        self.programName = program
        self.majorName = relatedMajor
        self.planType = self._plan_type()
        self.courseCodes = self._course_codes()
        self.additionalRequirement = additionalRequirement
        self.credits = credits

    def __str__(self):
        output = ""
        return output
