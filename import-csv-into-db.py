#!/usr/bin/env python
import getopt, sys
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
    if "import-csv-into-db.py" in inputFile:
      continue
    sqliteBackend.importFromCSVFile(db, inputFile)


if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    sys.exit()
