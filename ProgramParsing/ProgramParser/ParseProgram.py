from Database.DatabaseSender import DatabaseSender


def main(majorParser, files):
    dbc = DatabaseSender()

    dbc.execute("DROP TABLE" + " IF EXISTS " + dbc.requirements_table + " ;")
    dbc.create_requirements()

    for file in files:
        print("CURRENT FILE PARSING : " + file)
        parser = majorParser()
        parser.load_file(file)

        print(parser)

        # Parser requirement is a list of MajorReq Object
        dbc.insert_requirements(parser.requirement, "Math")
        dbc.commit()

    dbc.close()
