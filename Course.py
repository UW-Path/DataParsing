



class Course():

    def __init__(self, html):
        self.html = html
        self.code = html.find("a").get("name")
        '''self.prereqs = self.__get_prereqs(html)
        self.antireqs = self.__get_antireqs(html)
        self.info = self.__get_info(html)
        self.name = self.__get_name(html)
        self.id = self.__get_id(html)'''
        self.credit = self.__get_credit(html)
        #self.when = self.__get_when(html)
        self.online = any([isinstance(a.string, str) and a.string.endswith("Online") for a in html.find_all("a")])

    def __get_credit(self, html):
        print(html.find_all("b"))