#!/bin/sh

search_dir=./FTA_data/KOR
for entry in "$search_dir"/*
do
  echo "$entry"
  python table_to_latex.py "$entry" 0
done


search_dir=./FTA_data/EU
for entry in "$search_dir"/*
do
  echo "$entry"
  python table_to_latex.py "$entry" 1
done


search_dir=./FTA_data/US
for entry in "$search_dir"/*
do
  python table_to_latex.py "$entry" 2
done



