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
  echo "Parsing MATH degree requirements..."
  export PYTHONPATH=$PYTHONPATH:$DATAPARSING/ProgramParsing
  eval "${py} ProgramParsing/Math/UpdateDegreeRequirement.py > logs/UpdateDegreeRequirementMATH.log"
  echo "DONE"

  echo "===================================================="
  echo "Parsing MATH programs..."
  eval "${py} ProgramParsing/Math/ParseProgram.py > logs/ParseProgramMATH.log"
  echo "DONE"

  echo "===================================================="
  echo "Parsing MATH breadth and depth..."
  export PYTHONPATH=$PYTHONPATH:$DATAPARSING/BreadthDepthParsing
  eval "${py} BreadthDepthParsing/BreadthScript.py > logs/BreadthScriptMATH.log"
  echo "DONE"

  echo "===================================================="
  echo "Parsing Science degree requirements..."
  eval "${py} ProgramParsing/Science/UpdateDegreeRequirement.py > logs/UpdateDegreeRequirementSCI.log"
  echo "DONE"

  echo "===================================================="
  echo "Parsing Science programs..."
  eval "${py} ProgramParsing/Science/ParseProgram.py > logs/ParseProgramSCI.log"
  echo "DONE"

  echo "===================================================="
  echo "Parsing AHS degree requirements..."
  eval "${py} ProgramParsing/AHS/UpdateDegreeRequirement.py > logs/UpdateDegreeRequirementAHS.log"
  echo "DONE"

  echo "===================================================="
  echo "Parsing AHS programs..."
  eval "${py} ProgramParsing/AHS/ParseProgram.py > logs/ParseProgramAHS.log"
  echo "DONE"

  echo "===================================================="
  echo "Parsing Arts degree requirements..."
  eval "${py} ProgramParsing/Arts/UpdateDegreeRequirement.py > logs/UpdateDegreeRequirementARTS.log"
  echo "DONE"

  echo "===================================================="
  echo "Parsing Arts programs..."
  eval "${py} ProgramParsing/Arts/ParseProgram.py > logs/ParseProgramARTS.log"
  echo "DONE"

  echo "===================================================="
  echo "Parsing Engineering degree requirements..."
  eval "${py} ProgramParsing/Engineering/UpdateDegreeRequirement.py > logs/UpdateDegreeRequirementENG.log"
  echo "DONE"

  echo "===================================================="
  echo "Parsing Engineering programs..."
  eval "${py} ProgramParsing/Engineering/ParseProgram.py > logs/ParseProgramENG.log"
  echo "DONE"

  echo "===================================================="
  echo "Parsing Environment degree requirements..."
  eval "${py} ProgramParsing/Environment/UpdateDegreeRequirement.py > logs/UpdateDegreeRequirementENV.log"
  echo "DONE"

  echo "===================================================="
  echo "Parsing Environment programs..."
  eval "${py} ProgramParsing/Environment/ParseProgram.py > logs/ParseProgramENV.log"
  echo "DONE"
fi

echo "===================================================="
echo ""
echo "Check logs in Data-Parsing/logs"
