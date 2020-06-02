#!/bin/bash
echo "===================================================="
echo "Parsing courses..."
export PYTHONPATH=$PYTHONPATH:$DATAPARSING/CourseParsing
python CourseParsing/ParseScript.py > logs/ParseScript.log
echo "DONE"

echo "===================================================="
echo "Parsing communication tables..."
export PYTHONPATH=$PYTHONPATH:$DATAPARSING/CommunicationParsing
python CommunicationParsing/CommunicationScript.py > logs/CommunicationParsing.log
echo "DONE"

echo "===================================================="
echo "Parsing degree requirements..."
export PYTHONPATH=$PYTHONPATH:$DATAPARSING/ProgramParsing
python ProgramParsing/UpdateDegreeRequirement.py > logs/UpdateDegreeRequirement.log
echo "DONE"

echo "===================================================="
echo "Parsing programs..."
python ProgramParsing/ParseProgram.py > logs/ParseProgram.log
echo "DONE"

echo "===================================================="
echo "Parsing breadth and depth..."
export PYTHONPATH=$PYTHONPATH:$DATAPARSING/BreadthDepthParsing
python BreadthDepthParsing/BreadthScript.py > logs/BreadthScript.log
echo "DONE"

echo "===================================================="
echo ""
echo "Check logs in Data-Parsing/logs"
