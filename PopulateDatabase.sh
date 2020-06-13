#!/bin/bash

py="python"
courses=true
degree=true

while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "$package - attempt to capture frames"
      echo " "
      echo "$package [options] application [arguments]"
      echo " "
      echo "options:"
      echo "--python3     use python3"
      echo "--python      use python (default)"
      echo "--courses     only parse courses"
      echo "--degree      only parse degree"
      exit 0
      ;;
    --python3)
      shift
      py="python3"
      shift
      ;;
    --courses)
      shift
      degree=false
      shift
      ;;
    --degree)
      shift
      courses=false
      shift
      ;;
    *)
      break
      ;;
  esac
done

echo "Using python"
if $courses ;
then
  echo "===================================================="
  echo "Parsing courses..."
  export PYTHONPATH=$PYTHONPATH:$DATAPARSING/CourseParsing
  eval "${py} CourseParsing/ParseScript.py > logs/ParseScript.log"
  echo "DONE"

  echo "===================================================="
  echo "Parsing communication tables..."
  export PYTHONPATH=$PYTHONPATH:$DATAPARSING/CommunicationParsing
  eval "${py} CommunicationParsing/CommunicationScript.py > logs/CommunicationParsing.log"
  echo "DONE"
fi

if $degree ;
then
  echo "===================================================="
  echo "Parsing degree requirements..."
  export PYTHONPATH=$PYTHONPATH:$DATAPARSING/ProgramParsing
  eval "${py} ProgramParsing/Math/UpdateDegreeRequirement.py > logs/UpdateDegreeRequirementMATH.log"
  echo "DONE"

  echo "===================================================="
  echo "Parsing MATH programs..."
  eval "${py} ProgramParsing/Math/ParseProgram.py > logs/ParseProgramMATH.log"
  echo "DONE"

  echo "===================================================="
  echo "Parsing SCIENCE programs..."
  #eval "${py} ProgramParsing/Science/ParseProgram.py > logs/ParseProgramSCIENCE.log"
  echo "DONE"

  echo "===================================================="
  echo "Parsing breadth and depth..."
  export PYTHONPATH=$PYTHONPATH:$DATAPARSING/BreadthDepthParsing
  eval "${py} BreadthDepthParsing/BreadthScript.py > logs/BreadthScript.log"
  echo "DONE"
fi

echo "===================================================="
echo ""
echo "Check logs in Data-Parsing/logs"
