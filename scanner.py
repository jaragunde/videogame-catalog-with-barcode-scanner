#!/usr/bin/env python
import sys, subprocess


proc = subprocess.Popen(["zbarcam", "/dev/video2"],stdout=subprocess.PIPE)
while True:
  line = proc.stdout.readline()
  if not line:
    break
  
  name = sys.stdin.readline()
  print(line.decode('UTF-8').rstrip(), ":", name)
