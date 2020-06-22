from Database.DatabaseSender import DatabaseSender

def main(majorParser, files, faculty="Math", DropTable=False):
    dbc = DatabaseSender()
    if DropTable:
        dbc.execute("DROP TABLE IF EXISTS " + dbc.requirements_table + ";")
        dbc.create_requirements()

    for file in files:
        print("CURRENT FILE PARSING : " + file)
        parser = majorParser()
        parser.load_file(file)

        # Parser requirement is a list of MajorReq Object
        dbc.insert_requirements(parser.requirement, faculty)
        dbc.commit()

    dbc.close()
