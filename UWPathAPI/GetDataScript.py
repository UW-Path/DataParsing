from Database.DatabaseReceiver import DatabaseReceiver
from UWPathAPI.ValidationCheckAPI import ValidationCheckAPI

if __name__ == "__main__":
    dbc = DatabaseReceiver()
    api = ValidationCheckAPI(dbc)
    try:
        anti_req = api.get_course_anti_reqs("CS 341")

        print("Should be true:", end=" ")
        print(api.can_take_course(["CS 245", "ECE 406", "MATH 146", "MATH 138"],
                                  ["STAT 231"], "ACTSC 291"))

        print("coreq not met:", end=" ")
        print(api.can_take_course(["CS 245", "ECE 406", "MATH 146", "MATH 138"],
                                  ["STAT 230"], "ACTSC 291"))

        print("coreq met from previous term:", end=" ")
        print(api.can_take_course(["CS 245", "ECE 406", "MATH 146", "MATH 138", "STAT 231"],
                                  [], "ACTSC 291"))

        print("prereqs not met:", end=" ")
        print(api.can_take_course(["CS 245", "ECE 406", "MATH 138", "STAT 231"],
                                  [], "ACTSC 291"))

        print("prereqs not met because it is on same term:", end=" ")
        print(api.can_take_course(["CS 245", "ECE 406", "MATH 146", "STAT 231"],
                                  ["MATH 138"], "ACTSC 291"))

        print(dbc.select("*", "course_info"))
        print(dbc.select("*", "prereqs"))
        print(dbc.select("*", "coreqs"))
        print(dbc.select("*", "antireqs"))

        print(dbc.get_course_info())
        print(dbc.get_prereqs())
        print(dbc.get_coreqs())
        print(dbc.get_antireqs())

    except Exception as e:
        dbc.close()
        raise e
