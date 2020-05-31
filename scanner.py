#!/usr/bin/env python
import csv, sys, subprocess

# Configuration
defaultRegion = "ES"

csvFile = open("output.csv", mode='a')

proc = subprocess.Popen(["zbarcam", "/dev/video2"],stdout=subprocess.PIPE)

with open("output.csv", mode='a') as csvFile:
  csvWriter = csv.writer(csvFile)
  while True:
    line = proc.stdout.readline()
    if not line:
      break
    ean = line.decode('UTF-8').rstrip()
    print("Code read:", ean)

    print("Product name", end=": ", flush=True);
    name = sys.stdin.readline()

    print("Product ID", end=": ", flush=True);
    id = sys.stdin.readline()

    print("Region [default=", defaultRegion, "]", sep="", end=": ", flush=True)
    region = sys.stdin.readline().rstrip()
    if not region:
      region = defaultRegion

    print("Comments", end=": ", flush=True);
    comments = sys.stdin.readline()

    csvWriter.writerow([ean, name.rstrip(), id.rstrip(),
                        region.upper(), comments.rstrip()])

