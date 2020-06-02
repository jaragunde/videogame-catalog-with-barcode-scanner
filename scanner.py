#!/usr/bin/env python
import csv, sys, subprocess

# Configuration
command = ["zbarcam", "/dev/video2"]
#command = ["./fake-code.py"]
outputFile = "ps3.csv"
system = "PS3"
idPrefix = "BLES-"
defaultRegion = "ES"

def lookup(ean):
  ean = ean[-13:] # remove prefix 'EAN-13:'
  return "found in the internet"

def saveCSVRow(outputFile, row):
  with open(outputFile, mode='a') as csvFile:
    csv.writer(csvFile).writerow(row)

with subprocess.Popen(command, stdout=subprocess.PIPE) as proc:
  while True:
    line = proc.stdout.readline()
    if not line:
      break
    ean = line.decode('UTF-8').rstrip()
    print("Code read:", ean)

    print("Searching UPC database...", end=" ", flush=True)
    searchResult = lookup(ean)
    message = ""
    if searchResult:
      print("Match!")
      message = " [default=" + searchResult + "]"
    else:
      print("Not found")

    print("Product name", message, sep="", end=": ", flush=True);
    name = sys.stdin.readline().rstrip().title()
    if not name and searchResult:
      name = searchResult.title()

    print("Product ID [prefix=", idPrefix, "]", sep="", end=": ", flush=True)
    id = idPrefix + sys.stdin.readline().rstrip()

    print("Region [default=", defaultRegion, "]", sep="", end=": ", flush=True)
    region = sys.stdin.readline().rstrip().upper()
    if not region:
      region = defaultRegion

    print("Comments", end=": ", flush=True);
    comments = sys.stdin.readline().rstrip()

    saveCSVRow(outputFile, [system, ean, name, id, region, comments])

