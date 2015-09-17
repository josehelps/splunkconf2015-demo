#!/bin/bash

EXPECTED_ARGS=1
E_BADARGS=65

if [ $# -lt 1 ]
then
echo "Scripted input for splunk to monitors github changes locally"
echo "Usage: `basename $0` <path>"
echo "Example `basename $0`  /etc/ansible/"
echo ""
echo "path: of github hosted directory"
  exit $E_BADARGS
fi

if [ $# -gt $EXPECTED_ARGS ]
then
echo "Too many arguments"
        exit $E_BADARGS
fi

location=$1
cd $location 
if [ -a .changes ]
then
  git whatchanged > .current_changes
  diff .changes .current_changes -n
  mv .current_changes .changes
else
  git whatchanged > .changes
  cat .changes
fi

