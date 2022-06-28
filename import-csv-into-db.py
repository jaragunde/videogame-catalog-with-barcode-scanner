#!/usr/bin/env python
import csv, getopt, sys
import sqliteBackend

def printHelpAndExit():
  print("Usage: import-csv-into-db.py [OPTION]... [CSV FILE]...",
      "Import rows from CSV FILEs into the SQLite database stored in DB FILE.",
      "",
      "Options:",
      "  -h, --help                        Show help",
      "  -o [DB FILE], --output=[DB FILE]  REQUIRED. Output file with SQLite database.",
      sep="\n")
  sys.exit()


def importFromCSVFile(db, file):
  addAllDuplicates = False
  skipAllDuplicates = False

  with open(file) as csvFile:
    for row in csv.reader(csvFile):
      duplicate = sqliteBackend.findDuplicateEan(db, row[1])
      if duplicate:
        if skipAllDuplicates:
          continue
        elif not addAllDuplicates:
          print("Existing entry found in DB:",
              "EAN: %s" % duplicate["ean"],
              "System: %s" % duplicate["system"],
              "Name: %s" % duplicate["name"],
              "Product ID: %s" % duplicate["productid"],
              "Region: %s" % duplicate["region"],
              "Comment: %s" % duplicate["comment"],
              sep="\n\t", flush=True)
          print("Do you want to add a new, duplicate entry",
              "(yes/no/add all/skip all)? [y/n/a/s]", end=": ", flush=True)
          input = sys.stdin.readline().strip().upper()
          if input == "N":
            # skip to next row
            continue
          elif input == "S":
            skipAllDuplicates = True
            # skip to next row
            continue
          elif input == "A":
            addAllDuplicates = True
            # execute insert code below

      sqliteBackend.saveRow(db, row[0], row[1], row[2], row[3], row[4], row[5])


def main():
  databaseFile = ""
  inputFiles = []

  try:
    arguments, inputFiles = getopt.getopt(sys.argv[1:], "ho:", ["help", "output="])
    for currentArgument, currentValue in arguments:
        if currentArgument in ("-h", "--help"):
          printHelpAndExit()
        elif currentArgument in ("-o", "--output"):
          databaseFile = currentValue
  except getopt.error as err:
      # output error, and return with an error code
      print ("Error:", str(err))
      printHelpAndExit()

  if databaseFile == "":
    print("Error: missing output file argument.")
    printHelpAndExit()
  if len(inputFiles) == 0:
    print("Error: missing input CSV file(s).")
    printHelpAndExit()

  db = sqliteBackend.setupDatabaseFile(databaseFile)
  for inputFile in inputFiles:
    print("Processing file: ", inputFile)
    importFromCSVFile(db, inputFile)


if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    sys.exit()
