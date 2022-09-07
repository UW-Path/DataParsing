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
  export PYTHONPATH=$PWD
  eval "${py} ./CourseParsing/ParseScript.py" || { echo 'Parsing courses failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing communication tables..."
  export PYTHONPATH=$PYTHONPATH:/CommunicationParsing
  eval "${py} ./CommunicationParsing/CommunicationScript.py" || { echo 'Parsing communications failed' ; exit 1; }
  echo "DONE"
fi

if $degree ;
then
  export PYTHONPATH=$PYTHONPATH:/ProgramParsing
  export PYTHONWARNINGS="ignore:Unverified HTTPS request"

  echo "===================================================="
  echo "Parsing MATH degree requirements..."
  eval "${py} ./ProgramParsing/Math/UpdateDegreeRequirement.py" || { echo 'Parsing MATH degree requirements failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing MATH programs..."
  eval "${py} ProgramParsing/Math/ParseProgram.py" || { echo 'Parsing MATH programs failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing MATH breadth and depth..."
  export PYTHONPATH=$PYTHONPATH:/BreadthDepthParsing
  eval "${py} BreadthDepthParsing/BreadthScript.py" || { echo 'Parsing MATH programs failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing Science degree requirements..."
  eval "${py} ProgramParsing/Science/UpdateDegreeRequirement.py" || { echo 'Parsing Science degree requirements failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing Science programs..."
  eval "${py} ProgramParsing/Science/ParseProgram.py" || { echo 'Parsing Science programs failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing AHS degree requirements..."
  eval "${py} ProgramParsing/AHS/UpdateDegreeRequirement.py" || { echo 'Parsing AHS degree requirements failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing AHS programs..."
  eval "${py} ProgramParsing/AHS/ParseProgram.py" || { echo 'Parsing AHS programs failed ' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing Arts degree requirements..."
  eval "${py} ProgramParsing/Arts/UpdateDegreeRequirement.py" || { echo 'Parsing Arts degree requirements failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing Arts programs..."
  eval "${py} ProgramParsing/Arts/ParseProgram.py" || { echo 'Parsing Arts programs failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing Engineering degree requirements..."
  eval "${py} ProgramParsing/Engineering/UpdateDegreeRequirement.py" || { echo 'Parsing Engineering degree requirements failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing Engineering programs..."
  eval "${py} ProgramParsing/Engineering/ParseProgram.py" || { echo 'Parsing Engineering programs failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing Environment degree requirements..."
  eval "${py} ProgramParsing/Environment/UpdateDegreeRequirement.py" || { echo 'Parsing Environment degree requirements failed' ; exit 1; }
  echo "DONE"

  echo "===================================================="
  echo "Parsing Environment programs..."
  eval "${py} ProgramParsing/Environment/ParseProgram.py" || { echo 'Parsing Environment programs failed' ; exit 1; }
  echo "DONE"
fi

echo "===================================================="
echo "COMPLETED SUCCESSFULLY"
