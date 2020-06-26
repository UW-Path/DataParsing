# Data Parsing
This repository parse course data found on the University of Waterloo website and transfer that to UWPath's databases.

## Setup 
Python 3 and PostgreSQL


## Set up database
Make sure Postgres is setup: - Currently, only local server is available - Default Database Connection is: 'NAME': 'postgres', 'USER': 'postgres', 'PASSWORD': '1234', 'HOST': 'db', 'PORT': '5432'

## Set up Python
Go to the top level of the repo and run "pip install -r requirements.txt" on terminal. To populate database run "./PopulateDatabase.sh".

###### Refer to [wiki page](https://github.com/UW-Path/DataParsing/wiki/Developer:-Set-Up) for Docker setup
