"""
Course is an object class that stores information regarding a specific course.

Contributors:
Calder Lund
Hao Wei Huang
"""

import re
from CourseParsing.Requirements import Prereqs, Antireqs


class Course:
    def __init__(self, html):
        self.html = html
        self.course_code = ""
        self.course_number = ""
        self.course_abbr = ""
        self.__code()

        self.prereq_text = ""
        self.coreq_text = ""
        self.antireq_text = ""

        self.prereqs = self.__prereqs()
        self.antireqs = self.__antireqs()

        self.info = self.__info()
        self.name = self.__name()
        self.id = self.__id()
        self.credit = self.__credit()
        self.online = self.__online()
        self.offering = self.__offering()

    def __code(self):
        """
        Returns the course code.

        :return: string
        """
        # First occurrence always has course code
        course = self.html.find("a").get("name")
        code = re.findall("[A-Z]+", course)[0]
        num = course.strip(code)
        self.course_code = code + " " + num
        self.course_number = num
        self.course_abbr = code

    def __prereqs(self):
        """
        Returns a list of the course's required prerequisites.

        :return: list(str)
        """
        all_i = self.html.find_all("i")
        prereqs = Prereqs()
        for i in all_i:
            if i and i.string:
                string = i.string.replace("\n", " ").strip()
                if string.startswith("Prereq:"):
                    prereqs.load_prereqs(string, re.findall("[A-Z][A-Z]+", self.course_code)[0])
                    self.prereq_text = string.replace("Prereq:", "")
                elif string.startswith("Coreq:"):
                    prereqs.load_prereqs(string, re.findall("[A-Z][A-Z]+", self.course_code)[0])
                    self.coreq_text = string.replace("Coreq:", "")
        return prereqs

    def __antireqs(self):
        """
        Returns list of the course's anti-requisites.

        :return: list(str)
        """
        all_i = self.html.find_all("i")
        antireqs = Antireqs()
        for i in all_i:
            if i and i.string and i.string.strip().startswith("Antireq:"):
                string = i.string.strip().replace("\n", " ")
                antireqs.load_antireqs(string)
                self.antireq_text = string.replace("Antireq:", "")
                break
        return antireqs

    def __info(self):
        """
        Returns the entire description of the course.

        :return: string
        """
        return self.html.find_all("td")[3].string.strip("\n ").replace("'", "")

    def __name(self):
        """
        Returns the name of the course.

        :return: string
        """
        # Course name is always second occurrence
        return self.html.find_all("b")[1].string.replace("'", "")

    def __id(self):
        """
        Returns the course ID.

        :return: string
        """
        # self.html.find_all("td")[1] --> <td align="right">Course ID: XXXXXX</td>
        return self.html.find_all("td")[1].string.strip("Course ID: ").replace("'", "")

    def __credit(self):
        """
        Returns the amount of credit received for taking this course.

        :return: float
        """
        # Note:
        # str(self.html.find("b")) --> "<b><a name = "CS 123"></a>CS 123 LEC 0.50</b>"
        # str(self.html.find("b")).strip("</b>")[-4:] --> "0.50"
        return float(str(self.html.find("b")).strip("</b>")[-4:])

    def __online(self):
        """
        Returns whether the course is offered online.

        :return: boolean
        """
        # The online indicator will only ever appear as the last occurrence of a
        indicator = self.html.find_all("a")[-1]
        return isinstance(indicator.string, str) and indicator.string.endswith("Online")

    def __offering(self):
        """
        Returns the course offering for the given year in "F,W,S" format

        :return: string
        """
        # First occurrence always has course code
        filtered = re.search("(?<=Offered: ).*]", self.info)

        if filtered:
            # Should parse in F, W, S] string, ending in ]
            filtered = filtered.group()
            return filtered[:-1].split(",")
        else:
            # sometime it is in another line
            all_i = self.html.find_all("i")

            for i in all_i:
                if i and i.string and i.string.strip().startswith("[Note:"):
                    note = i.string.strip().replace("\n", " ")
                    filtered = re.search("(?<=Offered: ).*]", note)

                    if filtered:
                        # Should parse in F, W, S] string, ending in ]
                        filtered = filtered.group()
                        return filtered[:-1].split(",")
                    else:
                        return []
        return []

    def __str__(self):
        output = self.course_code + ": " + self.name

        if self.online:
            output += " (offered Online)"
        output += "\n"
        output += "\tCourse ID: " + self.id + "\tCourse credit: " + str(self.credit) + "\n"
        output += "\t" + self.info + "\n"

        if self.prereqs:
            output += self.prereqs.str("pretty")
        if self.antireqs:
            output += "Antireqs: " + self.antireqs.str() + "\n"
            output += self.antireqs.str("extra") + "\n"

        return output
