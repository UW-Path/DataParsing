from Database.DatabaseReceiver import DatabaseReceiver
from UWPathAPI.ValidationCheckApi import ValidationCheckApi

if __name__ == "__main__":
    dbc = DatabaseReceiver()
    api = ValidationCheckApi(dbc)

    try:
        anti_req = api.get_course_anti_reqs("CS 341")
        print(api.can_take_course(["CS 245", "ECE 406", "ACTSC 232"], "ACTSC 331"))
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
