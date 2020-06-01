#!/usr/bin/env python
import csv, sys, subprocess

# Configuration
videoDevice = "/dev/video2"
outputFile = "ps3.csv"
system = "PS3"
idPrefix = "BLES-"
defaultRegion = "ES"

proc = subprocess.Popen(["zbarcam", videoDevice],stdout=subprocess.PIPE)

with open(outputFile, mode='a') as csvFile:
  csvWriter = csv.writer(csvFile)
  while True:
    line = proc.stdout.readline()
    if not line:
      break
    ean = line.decode('UTF-8').rstrip()
    print("Code read:", ean)

    print("Product name", end=": ", flush=True);
    name = sys.stdin.readline().rstrip()

    print("Product ID [prefix=", idPrefix, "]", sep="", end=": ", flush=True)
    id = idPrefix + sys.stdin.readline().rstrip()

    print("Region [default=", defaultRegion, "]", sep="", end=": ", flush=True)
    region = sys.stdin.readline().rstrip().upper()
    if not region:
      region = defaultRegion

    print("Comments", end=": ", flush=True);
    comments = sys.stdin.readline().rstrip()

    csvWriter.writerow([system, ean, name, id, region, comments])

