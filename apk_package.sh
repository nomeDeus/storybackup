#!/bin/bash

test_project_name=$1
apk_file=$2
apk_test_file=$3
if [ -z $apk_file ]; then
	apk_file_num=`ls *.apk | wc -l | tr -d ' '`
	if [ $apk_file_num -gt 1 ]; then
		echo "Ambiguous apk_files. Please enter one APK to inspect."
		exit -1
	fi
	apk_file=`ls *.apk`
fi

mkdir uploads/temp/
mkdir uploads/temp/$test_project_name
mkdir uploads/temp/$test_project_name/apk_file
mkdir uploads/temp/$test_project_name/apk_test_file
mv uploads/$apk_file uploads/temp/$test_project_name/apk_file/$apk_file
mv uploads/$apk_test_file uploads/temp/$test_project_name/apk_test_file/$apk_test_file
rm -f -r uploads/temp
