from CommunicationParsing.MathCommunication import Communications
from Database.DatabaseSender import DatabaseSender

if __name__ == "__main__":
    com = Communications()
    com.load_file("MathReq.html")

    dbc = DatabaseSender()

    dbc.execute("DROP TABLE IF EXISTS " + dbc.communications_table + ";")
    dbc.create_communications()

    list1 = com.get_list1()
    list2 = com.get_list2()

    successes = 0
    failures = 0
    for code in list1:
        if dbc.insert_communication(code, 1):
            successes += 1
        else:
            failures += 1
        dbc.commit()

    for code in list2:
        if dbc.insert_communication(code, 2):
            successes += 1
        else:
            failures += 1
        dbc.commit()

    print("Successes:", successes)
    print("Failures: ", failures)

    dbc.close()
