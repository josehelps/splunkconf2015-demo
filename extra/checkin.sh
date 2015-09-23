#!/bin/bash

EXPECTED_ARGS=2
E_BADARGS=65

if [ $# -lt 2 ]
then
echo "script to commit changes via cronjob to git"
echo "Usage: `basename $0` <path> <branch>"
echo "Example `basename $0`  /opt/splunk/etc searchhead1"
echo ""
echo "path: of github hosted directory"
echo "branch: branch to commit to"
  exit $E_BADARGS
fi

if [ $# -gt $EXPECTED_ARGS ]
then
echo "Too many arguments"
        exit $E_BADARGS
fi

location=$1
date=`date`
branch=$2
cd $location
git add *
git commit -m 'checkin at $date'
git push origin $branch 
