"""
Major is an object class that stores information for major requirements

Contributors:
Hao Wei Huang
"""

from ProgramParsing.ProgramParser.MajorReq import MajorReq


class ScienceMajorReq(MajorReq):
    def __str__(self):
        output = "Requirement for: " + self.programName + " (" + self.planType + ")"
        output += "\n"
        output += "\tCourse (" + str(self.req) + ") : " + self.courseCodes + "\n"
        output += "\tCredits: " + str(self.credits)
        return output
