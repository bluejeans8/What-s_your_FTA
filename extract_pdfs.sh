#!/bin/sh

search_dir=./FTA_pdfs/EU
for entry in "$search_dir"/*
do
  echo "$entry"
  python extract_pdf.py "$entry"
done