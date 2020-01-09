from BreadthDepthParsing.Breadth import Breadth
from Database.DatabaseSender import DatabaseSender

if __name__ == "__main__":
    breadth = Breadth()
    file = "Breadth_and_depth.html"

    dbc = DatabaseSender()
    dbc.create_breadth()

    breadth.load_file(file)

    length = breadth.get_length()

    success = 0
    failure = 0
    for i in range(length):
        if dbc.insert_breadth(breadth.get_row(i)):
            success += 1
        else:
            failure += 1
        dbc.commit()

    print("Successes:", success)
    print("Failures: ", failure)

    dbc.close()
