"""
Parses information regarding how to satisfy breadth requirements.

Contributors:
Calder Lund
"""

import re

import pkg_resources
from bs4 import BeautifulSoup


class Breadth:
    def __init__(self):
        self.__subject         = []
        self.__name            = []
        self.__humanities      = []
        self.__social_science  = []
        self.__pure_science    = []
        self.__applied_science = []
        
        self.loaded = False
        self.data = None

    def load_file(self, file):
        html = pkg_resources.resource_string(__name__, file)
        # html = open(file, encoding="ISO-8859-1")

        self.data = BeautifulSoup(html, 'html.parser')
        breadth_table = self.data.find("tbody")
        course_types = breadth_table.find_all("tr")

        for course_type in course_types:
            data = course_type.find_all("td")

            for i, d in enumerate(data):
                d = d.text.strip()
                d = re.sub('[^a-zA-Z0-9 √]', '', d)

                if i == 0:
                    self.__subject.append(d)
                elif i == 1:
                    self.__name.append(d)
                elif i == 2:
                    self.__humanities.append(d == "√")
                elif i == 3:
                    self.__social_science.append(d == "√")
                elif i == 4:
                    self.__pure_science.append(d == "√")
                elif i == 5:
                    self.__applied_science.append(d == "√")
        
        self.loaded = True
                    
    def get_row(self, i):
        assert self.loaded
        return {"subject": self.__subject[i], "name": self.__name[i], "humanities": self.__humanities[i],
                "social_science": self.__social_science[i], "pure_science": self.__pure_science[i],
                "applied_science": self.__applied_science[i]}
    
    def get_length(self):
        assert self.loaded
        return len(self.__subject)
