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
        self.condition = "and"
        self.numberOfCourses = 1

    def update(self):
        self.planType = self._plan_type()
        self.courseCodes = " or ".join(self.list) if self.condition == "or" else ", ".join(self.list)
        self.numberOfCourses = len(self.list)

    def __str__(self):
        output = ""
        output += "Program:\t" + str(self.programName) + " (" + self.planType + ")\n"
        output += "Courses:\t" + str(self.courseCodes) + "\n"
        output += "Credits:\t" + str(self.credits)
        return output
