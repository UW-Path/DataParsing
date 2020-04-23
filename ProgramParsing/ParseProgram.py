from Database.DatabaseSender import DatabaseSender
from ProgramParsing.MajorParser import MajorParser
import os

if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    path = os.path.join(dir, 'ProgramSpecs')
    files = ["/ProgramSpecs/" + f for f in os.listdir(path) if f.endswith(".html")]
    files.append("TableII.html")

    #Update Files Not Parsable:
        # Data-Science.html, One of, Two of... not in <p>
        # ENG-Software-Engineering.html Different format
    #Need to Investigate
    filesToIgnore = ["MATH-Bachelor-of-Computer-Science-Data-Science.html", "ENG-Software-Engineering.html", "MATH-Math-or-Fin-Analysis-Risk-Mgt-Degree-Reqmnt.html"]
    filesToIgnore = ["/ProgramSpecs/" + f for f in filesToIgnore]

    # files = ["/ProgramSpecs/MATH-Math-or-Fin-Analysis-Risk-Mgt-Degree-Reqmnt.html"] #use this for single files



    # files = ["RequiredCSMajor.html", "RequiredActsciMajor.html", "RequiredCFMMajor.html", "RequiredSTATMajor.html",
    #          "RequiredAPPLIEDMajor.html", "RequiredAMATH-SCI-COMP-Major.html", "RequiredCOMajor.html",
    #          "RequiredPMATHTeachingMajor.html", "RequiredBiostatisticsMajor.html", "RequiredMATH-Finance-Major.html",
    #          "RequiredComputationalMATHMajor.html", "RequiredMATHStudiesMajor.html",
    #          "RequiredAISpecialization.html", "RequiredBioinformaticsSpecialization.html",
    #          "RequiredBusinessSpecialization.html", "RequiredFineArtSpecialization.html",
    #          "RequiredSoftwareSpecialization.html", "RequiredDigitalHardware.html", "RequiredACTSCIJoint.html",
    #          "RequiredAMATHJoint.html", "RequiredCSJoint.html",
    #          "RequiredACTSCI-FINANCE-Option.html", "TableII.html"]


    #Repeat program name
        #RequiredMATH - MS - Business - Specialization.html

    #below files are not parsable because "One of.."(or like the sorts) doesn not beong to a <p> tag
        #RequiredHumanComputerInteractionSpecialization.html
        #RequiredACTSCI-PredictiveAnalysis-Option.html
        #RequiredDATASciMajor.html
        #RequiredCOMajor.html (also "All of ..." followed by 2 courses, but english specifies only one or the other
    # below files are not parsable because COMPLETELY DIFF FORMAT
        #RequiredAMATHBiologySpecialization.html
        #RequiredAMATHEconSpecialization.html
        #Engineering Specialization: Heat and Mass Transfer
        #Physics Specialization
        #Mathematical Economics
        #Mathematics/Business Administration
        #Mathematics/Chartered Professional Accountancy (co-op only)
        #Mathematical Optimization has three different specialization in one page
        #Mathematics/Financial Analysis and Risk Management


    #Title has Degreee Requiremnt
        #Mathematical Economics
        #Information Technology Management

    #MINOR PROBLEM
    # "RequiredCOJoint.html" is not consistent... "Threee of" is not embedded in <p> MINOR
    # RequiredMATH-Finance-Major.html is not consistent "One of" is not in <p>
    # RequiredMATHCPAFINMajor.html (Mathematics/Chartered Professional Accountancy (co-op only)) "Two of" is not in <p>
    # RequiredPMATHJoint.html, Need to parse "Three additional PMATH courses. #TODO URGENT
    # "RequiredPMATHMajor.html" cannot get additional requirments
    # RequiredMATHTeachingMajor.html "Additional Req is not in <p> but in big <span>

    #Engineering Specialization: Communication and Control is not available
    #Joint Computer Science is not available

    #TODO parse which specialization is under which major

    dbc = DatabaseSender()

    dbc.create_requirements()

    for file in files:
        if (file in filesToIgnore): continue
        print("CURRENT FILE PARSING : " + file)
        parser = MajorParser()
        parser.load_file(file)

        print(parser)
        # Parser requirement is a list of MajorReq Object
        dbc.insert_requirements(parser.requirement)

        dbc.commit()

    dbc.close()