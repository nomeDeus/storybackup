#!/bin/bash

serial_number=$1

rm tmp

echo `adb -s $serial_number shell ps | grep com.example.android.testing.notes.mock | awk '{print $9}'` >> tmp
