"""
Major is an object class that stores information for major requirements

Contributors:
Hao Wei Huang
"""

from ProgramParsing.ProgramParser.MajorReq import MajorReq


class ScienceMajorReq(MajorReq):

    def __init__(self, list, numCourse, program, relatedMajor, additionalRequirement, credits):
        self.list = list
        self.programName = program
        self.majorName = relatedMajor
        self.planType = self._plan_type()
        self.additional = 0 # not used
        self.courseCodes = self._course_codes()
        self.numberOfCourses = numCourse
        self.additionalRequirement = additionalRequirement
        self.credits = credits

    def __str__(self):
        output = "Requirement for: " + self.programName + " (" + self.planType + ")"
        output += "\n"
        output += "\tCourse (" + str(self.req) + ") : " + self.courseCodes + "\n"
        output += "\tCredits: " + str(self.credits)
        return output
