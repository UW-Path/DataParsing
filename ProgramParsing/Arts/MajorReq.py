"""
Major is an object class that stores information for major requirements

Contributors:
Calder Lund
"""

from ProgramParsing.ProgramParser.MajorReq import MajorReq
from StringToNumber import StringToNumber


class ArtsMajorReq(MajorReq):
    def __number_of_courses(self):
        """
                Returns courses needed for the group of course_codes

                :return: int
        """
        if self.req == "All of":
            length = len(self.courseCodes.split(","))
            return length
        elif self.req == "Additional":
            return self.additional
        else:
            return StringToNumber[str(self.req).lower().split(' ')[0]].value[0]

    def __str__(self):
        output = "Requirement for: " + self.programName + " (" + self.planType + ")"
        output += "\n"
        if self.req == "Additional":
            output += "\tCourse (" + self.req + " " + str(self.additional) + ") : " + self.courseCodes + "\n"
        else:
            output += "\tCourse (" + self.req + ") : " + self.courseCodes + "\n"
        return output