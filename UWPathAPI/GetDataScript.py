from Database.DatabaseReceiver import DatabaseReceiver

if __name__ == "__main__":
    dbc = DatabaseReceiver()

    try:
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
