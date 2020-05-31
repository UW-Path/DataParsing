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

## Django ##
Make sure local database is setup under django_projects/settings.py under var DATABASES (Verify localhost, port, username password is correct)

open UWPathWebsite on cmd and run the following commands:

python manage.py makemigrations
python manage.py migrate

Run below command to start the webpage:
python manage.py runserver

To set up email notification: 
- Setup env variable for under variable name UWPath_Email_Account and UWPath_Email_Password


