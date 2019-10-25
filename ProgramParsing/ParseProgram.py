from Database import DatabaseConnection
from ProgramParsing.MajorParser import MajorParser

if __name__ == "__main__":
    files = ["RequiredCSMajor.html", "RequiredActsciMajor.html", "RequiredCFMMajor.html",
             "RequiredAISpecialization.html", "RequiredBioinformaticsSpecialization.html",
             "RequiredBusinessSpecialization.html", "RequiredFineArtSpecialization.html",
             "RequiredSoftwareSpecialization.html", "RequiredDigitalHardware.html"]
    #RequiredHumanComputerInteractionSpecialization.html not doable
    #files = ["RequiredCSMajor.html"] #use this for single files

    dbc = DatabaseConnection()

    dbc.create_requirements()

    for file in files:
        parser = MajorParser()
        parser.load_file(file)

        print(parser)

        # Parser requirement is a list of MajorReq Object
        dbc.insert_requirements(parser.requirement)

        dbc.commit()

    dbc.close()