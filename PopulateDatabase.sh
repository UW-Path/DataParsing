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
  export PYTHONPATH=$PWD/DataParsing
  eval "${py} DataParsing/CourseParsing/ParseScript.py"
  echo "DONE"

  echo "===================================================="
  echo "Parsing communication tables..."
  export PYTHONPATH=$PYTHONPATH:$DATAPARSING/CommunicationParsing
  eval "${py} DataParsing/CommunicationParsing/CommunicationScript.py"
  echo "DONE"
fi

if $degree ;
then
  export PYTHONPATH=$PYTHONPATH:$DATAPARSING/ProgramParsing
  export PYTHONWARNINGS="ignore:Unverified HTTPS request"

  echo "===================================================="
  echo "Parsing MATH degree requirements..."
  eval "${py} DataParsing/ProgramParsing/Math/UpdateDegreeRequirement.py" || { echo 'Parsing MATH degree requirements failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing MATH programs..."
  eval "${py} DataParsing/ProgramParsing/Math/ParseProgram.py" || { echo 'Parsing MATH programs failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing MATH breadth and depth..."
  export PYTHONPATH=$PYTHONPATH:$DATAPARSING/BreadthDepthParsing
  eval "${py} DataParsing/BreadthDepthParsing/BreadthScript.py" || { echo 'Parsing MATH programs failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing Science degree requirements..."
  eval "${py} DataParsing/ProgramParsing/Science/UpdateDegreeRequirement.py" || { echo 'Parsing Science degree requirements failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing Science programs..."
  eval "${py} DataParsing/ProgramParsing/Science/ParseProgram.py" || { echo 'Parsing Science programs failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing AHS degree requirements..."
  eval "${py} DataParsing/ProgramParsing/AHS/UpdateDegreeRequirement.py" || { echo 'Parsing AHS degree requirements failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing AHS programs..."
  eval "${py} DataParsing/ProgramParsing/AHS/ParseProgram.py" || { echo 'Parsing AHS programs failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing Arts degree requirements..."
  eval "${py} DataParsing/ProgramParsing/Arts/UpdateDegreeRequirement.py" || { echo 'Parsing Arts degree requirements failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing Arts programs..."
  eval "${py} DataParsing/ProgramParsing/Arts/ParseProgram.py" || { echo 'Parsing Arts programs failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing Engineering degree requirements..."
  eval "${py} DataParsing/ProgramParsing/Engineering/UpdateDegreeRequirement.py" || { echo 'Parsing Engineering degree requirements failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing Engineering programs..."
  eval "${py} DataParsing/ProgramParsing/Engineering/ParseProgram.py" || { echo 'Parsing Engineering programs failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing Environment degree requirements..."
  eval "${py} DataParsing/ProgramParsing/Environment/UpdateDegreeRequirement.py" || { echo 'Parsing Environment degree requirements failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing Environment programs..."
  eval "${py} DataParsing/ProgramParsing/Environment/ParseProgram.py" || { echo 'Parsing Environment programs failed' ; exit 1; }
  echo "DONE"
fi

echo "===================================================="
echo "COMPLETED"
