#!/bin/bash

EXPECTED_ARGS=1
E_BADARGS=65

if [ $# -lt 1 ]
then
echo "script to commit changes via cronjob to git"
echo "Usage: `basename $0` <path>"
echo "Example `basename $0`  /opt/splunk/etc"
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
date=`date`
cd $location
git add *
git commit -m 'checkin at $date'
git push origin master
