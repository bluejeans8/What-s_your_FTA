#!/bin/sh

search_dir=./FTA_pdfs/EU
for entry in "$search_dir"/*
do
  python extract_pdf.py "$entry" 1
done


search_dir=./FTA_pdfs/US
for entry in "$search_dir"/*
do
  python extract_pdf.py "$entry" 2
done


search_dir=./FTA_pdfs/KOR
for entry in "$search_dir"/*
do
  echo "$entry"
  python extract_pdf.py "$entry" 0
done




