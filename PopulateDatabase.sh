#!/bin/bash
if [ -z "$1" ] || [ "$1" != "--python3" ]
then
  echo "Using python"
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
  python ProgramParsing/Math/ParseProgram.py > logs/ParseProgram.log
  echo "DONE"

  echo "===================================================="
  echo "Parsing breadth and depth..."
  export PYTHONPATH=$PYTHONPATH:$DATAPARSING/BreadthDepthParsing
  python BreadthDepthParsing/BreadthScript.py > logs/BreadthScript.log
  echo "DONE"

else
  echo "Using python3"
  echo "===================================================="
  echo "Parsing courses..."
  export PYTHONPATH=$PYTHONPATH:$DATAPARSING/CourseParsing
  python3 CourseParsing/ParseScript.py > logs/ParseScript.log
  echo "DONE"

  echo "===================================================="
  echo "Parsing communication tables..."
  export PYTHONPATH=$PYTHONPATH:$DATAPARSING/CommunicationParsing
  python3 CommunicationParsing/CommunicationScript.py > logs/CommunicationParsing.log
  echo "DONE"

  echo "===================================================="
  echo "Parsing degree requirements..."
  export PYTHONPATH=$PYTHONPATH:$DATAPARSING/ProgramParsing
  python3 ProgramParsing/UpdateDegreeRequirement.py > logs/UpdateDegreeRequirement.log
  echo "DONE"

  echo "===================================================="
  echo "Parsing programs..."
  python3 ProgramParsing/ParseProgram.py > logs/ParseProgram.log
  echo "DONE"

  echo "===================================================="
  echo "Parsing breadth and depth..."
  export PYTHONPATH=$PYTHONPATH:$DATAPARSING/BreadthDepthParsing
  python3 BreadthDepthParsing/BreadthScript.py > logs/BreadthScript.log
  echo "DONE"
fi

echo "===================================================="
echo ""
echo "Check logs in Data-Parsing/logs"
