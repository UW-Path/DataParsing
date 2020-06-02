<img src="demo.png?raw=true"/>
</br>

<b>UWPath is a website that helps University of Waterloo students plan their future courses according to their majors/minors/specific courses/etc. <b/>


# Set Up#
Refer to requirements.txt for all the Python modules needed. Project is built with Python 3.8.

## Backend ##
1. Make sure Postgres is setup:
    - Currently, only local server is available
    - Default Database Connection is:
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '8888'
2. Run the following script to load all parse tables (in order)
    - CommunicationParsing/CommunicationScript.py
    - CourseParsing/CourseParser.py
    - ProgramParsing/UpdateDegreeRequirement.py
    - ProgramParsing/ParseProgram.py
    - BreadthDepthParsing/BreadthScript.py



