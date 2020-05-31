#!/usr/bin/env python
import sys, subprocess

csvFile = open("output.csv", mode='a')

proc = subprocess.Popen(["zbarcam", "/dev/video2"],stdout=subprocess.PIPE)
while True:
  ean = proc.stdout.readline()
  if not ean:
    break

  print("Product name", end=": ", flush=True);
  name = sys.stdin.readline()
  print("Product ID", end=": ", flush=True);
  id = sys.stdin.readline()
  print("Comments", end=": ", flush=True);
  comments = sys.stdin.readline()
  print(ean.decode('UTF-8').rstrip(), name.rstrip(), id.rstrip(),
        comments.rstrip(), sep=",", file=csvFile)

csvFile.close()
