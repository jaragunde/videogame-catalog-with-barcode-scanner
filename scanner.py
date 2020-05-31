#!/usr/bin/env python
import sys, subprocess

csvFile = open("output.csv", mode='a')

proc = subprocess.Popen(["zbarcam", "/dev/video2"],stdout=subprocess.PIPE)

with open("output.csv", mode='a') as csvFile:
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
    print("Comments", end=": ", flush=True);
    comments = sys.stdin.readline()
    print(ean, name.rstrip(), id.rstrip(),
          comments.rstrip(), sep=",", file=csvFile)

