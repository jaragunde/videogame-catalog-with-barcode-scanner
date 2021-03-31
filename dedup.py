#!/usr/bin/env python
import csv, sqlite3, sys, subprocess

##### Configuration

# General setup
command = ["zbarcam", "/dev/video2"] # Fetch EANs with the zbarcam tool
#command = ["./fake-code.py"] # Fake EAN generation, useful for testing
#command = False # Set False to type EANs manually
outputFile = "output.csv"

def setupDatabaseFromFile(db, file):
  db.execute("CREATE TABLE games(name TEXT NOT NULL, ean INT NOT NULL)")

  with open(file) as csvFile:
    for row in csv.reader(csvFile):
      ean = row[1]
      if ean.startswith("EAN-13:"):
        ean = ean[-13:] # remove prefix
      db.execute("INSERT INTO games (ean, name) VALUES (?,?)", (ean, row[2]))

  print("DB setup from file", file)

def processEntry(eanInputFile, db):
  ean = eanInputFile.readline().rstrip()
  if not ean:
    return False
  if ean.startswith("EAN-13:"):
    ean = ean[-13:] # remove prefix
  print("EAN:", ean, end=" ", flush=True)

  row = db.execute('SELECT ean, name FROM games WHERE EAN=?', (ean,)).fetchone()
  if row:
    print("Found:", row[1])
  else:
    print("Not found")

  return True

def main():
  db = sqlite3.connect(":memory:")
  setupDatabaseFromFile(db, outputFile)
  if command:
    with subprocess.Popen(command, stdout=subprocess.PIPE,
        encoding='UTF-8') as proc:
      while True:
        # Loop until there's no more ean data from subprocess
        if not processEntry(proc.stdout, db):
          break
  else:
    while True:
      print("EAN code (empty to exit)", end=": ", flush=True)
      if not processEntry(sys.stdin, db):
        break


if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    sys.exit()
